"""Load and validate ``driftguard.toml``. Every path in the config is relative to the file's own
directory, so the tool behaves the same from any working directory."""

from __future__ import annotations

import fnmatch
import glob as globmod
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(Exception):
    pass


TOP_KEYS = {
    "docs", "exclude", "plugins", "supersede_markers", "legacy", "id_classes", "templates",
    "banned", "leaks", "adoption", "currency", "registries",
}
DEFAULT_MARKERS = ["superseded-by", "supersedes"]
DEFAULT_LEGACY = [{"name": "section ordinal", "pattern": r"§\d"}]
KINDS = {"table", "build_plan", "id_register"}
SLICES = {"phase", "status", "none"}
DEFAULT_STATUS_LABELS = {"pass": "Fixed", "fail": "Confirmed-Open", "decision": "WontFix"}


def _rx(value: object, where: str) -> re.Pattern[str]:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{where}: expected a regex string, got {value!r}")
    try:
        return re.compile(value, re.M)
    except re.error as e:
        raise ConfigError(f"{where}: bad regex {value!r}: {e}") from None


def _list(value: object, where: str, default: list | None = None) -> list:
    if value is None:
        return list(default or [])
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise ConfigError(f"{where}: expected a list, got {type(value).__name__}")
    return list(value)


def _fnmatch(rel: str, pattern: str) -> bool:
    if fnmatch.fnmatch(rel, pattern):
        return True
    # fnmatch has no ``**``; a pattern like ``docs/**/*.md`` must also match ``docs/a.md``.
    return "**/" in pattern and fnmatch.fnmatch(rel, pattern.replace("**/", ""))


@dataclass
class IdClass:
    name: str
    ref: re.Pattern[str]
    definition: re.Pattern[str]
    def_files: list[str]
    def_prefix: str
    filename_must_match: bool
    allocate: bool
    ears: bool
    ignore: set[str]


@dataclass
class Config:
    root: Path
    path: Path
    docs: list[str]
    exclude: list[str]
    plugins: list[str]
    supersede_markers: list[str]
    legacy: list[dict]
    id_classes: list[IdClass]
    templates: list[dict]
    banned: list[dict]
    leaks: dict | None
    adoption: list[dict]
    currency: dict | None
    registries: list[dict]
    _files_cache: dict = field(default_factory=dict, repr=False)

    # -- paths ---------------------------------------------------------------------------------
    def rel(self, p: str | Path) -> str:
        return Path(p).resolve().relative_to(self.root).as_posix()

    def abs(self, rel: str) -> Path:
        return (self.root / rel).resolve()

    def expand(self, patterns: list[str]) -> list[str]:
        out: set[str] = set()
        for pat in patterns:
            for hit in globmod.glob(str(self.root / pat), recursive=True):
                p = Path(hit)
                if p.is_file():
                    out.add(p.resolve().relative_to(self.root).as_posix())
        return sorted(out)

    def matches(self, rel: str, patterns: list[str] | str) -> bool:
        pats = [patterns] if isinstance(patterns, str) else patterns
        return any(_fnmatch(rel, p) for p in pats)

    def doc_files(self) -> list[str]:
        return [f for f in self.expand(self.docs) if not self.matches(f, self.exclude)]

    def read(self, rel: str) -> str:
        return self.abs(rel).read_text(encoding="utf-8", errors="replace")

    def class_named(self, name: str) -> IdClass | None:
        return next((c for c in self.id_classes if c.name == name), None)

    def is_generated(self, rel: str) -> bool:
        """A registry's rendered output (index or slice) is a view, not authored prose: it cites
        every ID and must not count as a backlink or a stale citation."""
        for reg in self.registries:
            out = reg["output"]
            if rel == out or rel.startswith(Path(out).with_suffix("").as_posix() + "/"):
                return True
        return False


def _id_class(raw: dict, i: int) -> IdClass:
    where = f"id_classes[{i}]"
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: expected a table")
    name = raw.get("name")
    if not isinstance(name, str) or not name:
        raise ConfigError(f"{where}: 'name' is required")
    unknown = set(raw) - {"name", "ref", "def", "def_files", "def_prefix", "filename_must_match",
                          "allocate", "ears", "ignore"}
    if unknown:
        raise ConfigError(f"{where} ({name}): unknown keys {sorted(unknown)}")
    return IdClass(
        name=name,
        ref=_rx(raw.get("ref"), f"{where}.ref"),
        definition=_rx(raw.get("def"), f"{where}.def"),
        def_files=_list(raw.get("def_files"), f"{where}.def_files"),
        def_prefix=str(raw.get("def_prefix", "")),
        filename_must_match=bool(raw.get("filename_must_match", False)),
        allocate=bool(raw.get("allocate", False)),
        ears=bool(raw.get("ears", False)),
        ignore=set(_list(raw.get("ignore"), f"{where}.ignore")),
    )


def _template(raw: dict, i: int, docs: list[str]) -> dict:
    where = f"templates[{i}]"
    unknown = set(raw) - {"match", "required", "complete_tables", "assumptions_table"}
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
    match = _list(raw.get("match"), f"{where}.match")
    if not match:
        raise ConfigError(f"{where}: 'match' is required")
    return {
        "match": match,
        "required": _list(raw.get("required"), f"{where}.required"),
        "complete_tables": _list(raw.get("complete_tables"), f"{where}.complete_tables"),
        "assumptions_table": raw.get("assumptions_table"),
    }


def _banned(raw: dict, i: int, docs: list[str]) -> dict:
    where = f"banned[{i}]"
    unknown = set(raw) - {"pattern", "message", "files", "except"}
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
    return {
        "pattern": _rx(raw.get("pattern"), f"{where}.pattern"),
        "message": str(raw.get("message") or "banned pattern"),
        "files": _list(raw.get("files"), f"{where}.files", docs),
        "except": [_rx(x, f"{where}.except") for x in _list(raw.get("except"), f"{where}.except")],
    }


def _adoption(raw: dict, i: int) -> dict:
    where = f"adoption[{i}]"
    unknown = set(raw) - {"name", "pattern", "glob", "allow_files", "justification_pattern", "message"}
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
    jp = raw.get("justification_pattern")
    return {
        "name": str(raw.get("name") or f"rule-{i}"),
        "pattern": _rx(raw.get("pattern"), f"{where}.pattern"),
        "glob": _list(raw.get("glob"), f"{where}.glob", ["**/*"]),
        "allow_files": _list(raw.get("allow_files"), f"{where}.allow_files"),
        "justification": _rx(jp, f"{where}.justification_pattern") if jp else None,
        "message": str(raw.get("message") or "use the shared helper"),
    }


def _registry(raw: dict, i: int) -> dict:
    where = f"registries[{i}]"
    unknown = set(raw) - {"name", "kind", "source", "output", "slice_by", "runner", "pass_code",
                          "fail_code", "status_labels", "columns", "id_pattern", "strict_coverage",
                          "discharges_class", "require_tier2", "backlinks", "title"}
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
    kind = raw.get("kind")
    if kind not in KINDS:
        raise ConfigError(f"{where}: kind must be one of {sorted(KINDS)}, got {kind!r}")
    name = raw.get("name") or kind
    if kind != "id_register" and not raw.get("source"):
        raise ConfigError(f"{where} ({name}): 'source' is required for kind={kind}")
    if not raw.get("output"):
        raise ConfigError(f"{where} ({name}): 'output' is required")
    slice_by = raw.get("slice_by", "none")
    if slice_by not in SLICES:
        raise ConfigError(f"{where} ({name}): slice_by must be one of {sorted(SLICES)}")
    columns = raw.get("columns")
    if columns is not None and not all(isinstance(c, list) and len(c) == 2 for c in columns):
        raise ConfigError(f"{where} ({name}): columns must be [[header, key], ...]")
    return {
        "name": name,
        "kind": kind,
        "source": raw.get("source"),
        "output": raw["output"],
        "slice_by": slice_by,
        "runner": _list(raw.get("runner"), f"{where}.runner", ["pytest", "-q"]),
        "pass_code": int(raw.get("pass_code", 0)),
        "fail_code": int(raw.get("fail_code", 1)),
        "status_labels": {**DEFAULT_STATUS_LABELS, **(raw.get("status_labels") or {})},
        "columns": columns,
        "id_pattern": _rx(raw.get("id_pattern", r"^[A-Z]+-\d+$"), f"{where}.id_pattern"),
        "strict_coverage": bool(raw.get("strict_coverage", False)),
        "discharges_class": str(raw.get("discharges_class", "REQ")),
        "require_tier2": bool(raw.get("require_tier2", False)),
        "backlinks": bool(raw.get("backlinks", False)),
        "title": raw.get("title"),
    }


def load(path: str | Path) -> Config:
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"config not found: {p}")
    try:
        raw = tomllib.loads(p.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{p}: {e}") from None
    unknown = set(raw) - TOP_KEYS
    if unknown:
        raise ConfigError(f"{p}: unknown top-level keys {sorted(unknown)}")
    docs = _list(raw.get("docs"), "docs")
    if not docs:
        raise ConfigError(f"{p}: 'docs' (list of globs) is required")
    legacy = []
    for i, item in enumerate(_list(raw.get("legacy"), "legacy", DEFAULT_LEGACY)):
        if not isinstance(item, dict) or "pattern" not in item:
            raise ConfigError(f"legacy[{i}]: expected {{name, pattern}}")
        legacy.append({"name": str(item.get("name") or f"legacy-{i}"),
                       "pattern": _rx(item["pattern"], f"legacy[{i}].pattern")})
    leaks = raw.get("leaks")
    if leaks is not None:
        unknown = set(leaks) - {"globs", "id_pattern"}
        if unknown:
            raise ConfigError(f"leaks: unknown keys {sorted(unknown)}")
        leaks = {"globs": _list(leaks.get("globs"), "leaks.globs"),
                 "id_pattern": _rx(leaks["id_pattern"], "leaks.id_pattern") if leaks.get("id_pattern") else None}
    currency = raw.get("currency")
    if currency is not None:
        unknown = set(currency) - {"docs", "claim_pattern", "path_pattern"}
        if unknown:
            raise ConfigError(f"currency: unknown keys {sorted(unknown)}")
        currency = {
            "docs": _list(currency.get("docs"), "currency.docs", docs),
            "claim": _rx(currency.get("claim_pattern", r"(?i)\b(still|not yet|pending|outstanding|unresolved|for now)\b"), "currency.claim_pattern"),
            "path": _rx(currency.get("path_pattern", r"`([\w./-]+\.[A-Za-z0-9]+)`"), "currency.path_pattern"),
        }
    cfg = Config(
        root=p.resolve().parent,
        path=p.resolve(),
        docs=docs,
        exclude=_list(raw.get("exclude"), "exclude"),
        plugins=_list(raw.get("plugins"), "plugins"),
        supersede_markers=_list(raw.get("supersede_markers"), "supersede_markers", DEFAULT_MARKERS),
        legacy=legacy,
        id_classes=[_id_class(c, i) for i, c in enumerate(_list(raw.get("id_classes"), "id_classes"))],
        templates=[_template(t, i, docs) for i, t in enumerate(_list(raw.get("templates"), "templates"))],
        banned=[_banned(b, i, docs) for i, b in enumerate(_list(raw.get("banned"), "banned"))],
        leaks=leaks,
        adoption=[_adoption(a, i) for i, a in enumerate(_list(raw.get("adoption"), "adoption"))],
        currency=currency,
        registries=[_registry(r, i) for i, r in enumerate(_list(raw.get("registries"), "registries"))],
    )
    names = [c.name for c in cfg.id_classes]
    if len(names) != len(set(names)):
        raise ConfigError(f"{p}: duplicate id_classes names")
    return cfg
