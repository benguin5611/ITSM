"""Scan the doc set once: definitions and references per ID class, tombstones, titles, legacy
tokens. Also the git seam (changed files, added lines, file content at a ref) so diff-scoped
checks share one implementation."""

from __future__ import annotations

import collections
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import Finding
from .config import Config, IdClass

FRONTMATTER_RX = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.S)
STATUS_TOMB_RX = re.compile(r"(?m)^status:\s*(superseded-by\b.*|removed\b.*)$")
HEADING_RX = re.compile(r"(?m)^(#{1,6})\s+(.*?)\s*$")
COMMENT_RX = re.compile(r"<!--.*?-->", re.S)


def run_cmd(argv: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """The one subprocess seam; tests replace it."""
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def frontmatter(text: str) -> tuple[str, int]:
    """Return (frontmatter body, number of lines it occupies including fences) or ('', 0)."""
    m = FRONTMATTER_RX.match(text)
    if not m:
        return "", 0
    return m.group(1), m.group(0).count("\n")


def _title_for(line: str, ident: str) -> str:
    """The human title on a definition line: the line minus the ID, bold, heading marks, a leading
    parenthetical such as ``(Ubiquitous)`` or ``(Phase 0)``, and punctuation. For a table row, the
    first non-empty cell after the ID."""
    s = line.replace(ident, "", 1)
    if s.lstrip().startswith("|"):
        cells = [c.strip() for c in s.strip().strip("|").split("|")]
        s = next((c for c in cells if c), "")
    s = re.sub(r"<!--.*?-->", "", s.replace("**", ""))
    s = re.sub(r"^\s*#+\s*", "", s)
    s = re.sub(r"^[\s—–\-:.|]*(?:\([^)]*\))?[\s—–\-:.|]*", "", s)
    return s.strip().rstrip(" .*|")


@dataclass
class DocSet:
    cfg: Config
    files: list[str]
    text: dict[str, str]
    defs: dict[str, collections.Counter] = field(default_factory=dict)
    def_sites: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    refs: dict[str, dict[str, list[tuple[str, int]]]] = field(default_factory=dict)
    tombstones: set[str] = field(default_factory=set)
    titles: dict[str, str] = field(default_factory=dict)
    cls_of: dict[str, str] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def defined(self, ident: str) -> bool:
        return ident in self.cls_of

    def all_ids(self, cls: str) -> list[str]:
        return sorted(self.defs.get(cls, {}))

    def referenced_from(self, ident: str) -> list[str]:
        cls = self.cls_of.get(ident)
        if cls is None:
            return []
        own = {p for p, _ in self.def_sites.get(ident, [])}
        return sorted({p for p, _ in self.refs.get(cls, {}).get(ident, [])
                       if p not in own and not self.cfg.is_generated(p)})


def _scan_defs(ds: DocSet, ic: IdClass, path: str, text: str, tomb_all: bool) -> None:
    if ic.def_files and not ds.cfg.matches(path, ic.def_files):
        return
    for m in ic.definition.finditer(text):
        ident = ic.def_prefix + m.group(1)
        if ident in ic.ignore:
            continue
        ln = line_of(text, m.start())
        ds.defs.setdefault(ic.name, collections.Counter())[ident] += 1
        ds.def_sites.setdefault(ident, []).append((path, ln))
        ds.cls_of.setdefault(ident, ic.name)
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        line = text[line_start: len(text) if line_end < 0 else line_end]
        ds.titles.setdefault(ident, _title_for(line, m.group(1)))
        if ic.filename_must_match and not Path(path).stem.startswith(ident):
            ds.findings.append(Finding(path, ln, "DG-FILENAME",
                               f"{ident} is defined in a file whose name does not start with it"))
        if tomb_all:
            ds.tombstones.add(ident)


def _scan_refs(ds: DocSet, ic: IdClass, path: str, text: str) -> None:
    bucket = ds.refs.setdefault(ic.name, {})
    for m in ic.ref.finditer(text):
        ident = m.group(0)
        if ident in ic.ignore:
            continue
        bucket.setdefault(ident, []).append((path, line_of(text, m.start())))


def _scan_tombstones(ds: DocSet, path: str, text: str) -> None:
    """``X … superseded-by Y`` tombstones X (the ID before the marker); ``Y supersedes X``
    tombstones X (the ID after). In a table row the whole row before/after the marker counts;
    in prose only the nearest 80 characters do."""
    if not ds.cfg.id_classes:
        return
    any_ref = re.compile("|".join(f"(?:{ic.ref.pattern})" for ic in ds.cfg.id_classes))
    for line in text.split("\n"):
        table = line.lstrip().startswith("|")
        for m in re.finditer(r"superseded-by\b", line):
            head = line[: m.start()] if table else line[max(0, m.start() - 80): m.start()]
            ds.tombstones.update(x.group(0) for x in any_ref.finditer(head))
        for m in re.finditer(r"\bsupersedes\b", line):
            tail = line[m.end():] if table else line[m.end(): m.end() + 80]
            ds.tombstones.update(x.group(0) for x in any_ref.finditer(tail))


def scan(cfg: Config, files: list[str] | None = None, text: dict[str, str] | None = None) -> DocSet:
    files = sorted(files if files is not None else cfg.doc_files())
    text = text if text is not None else {f: cfg.read(f) for f in files}
    ds = DocSet(cfg=cfg, files=files, text=text)
    for ic in cfg.id_classes:
        ds.defs.setdefault(ic.name, collections.Counter())
        ds.refs.setdefault(ic.name, {})
    for path in files:
        body = text[path]
        fm, _ = frontmatter(body)
        tomb_all = bool(STATUS_TOMB_RX.search(fm)) if fm else False
        for ic in cfg.id_classes:
            _scan_defs(ds, ic, path, body, tomb_all)
            _scan_refs(ds, ic, path, body)
        _scan_tombstones(ds, path, body)
        for rule in cfg.legacy:
            for m in rule["pattern"].finditer(body):
                ds.findings.append(Finding(path, line_of(body, m.start()), "DG-LEGACY",
                                           f"legacy token ({rule['name']}): {m.group(0)!r}"))
    return ds


# -- git seam --------------------------------------------------------------------------------------


class DiffError(Exception):
    pass


class Diff:
    """Changed files and added lines for ``--staged`` (index vs HEAD) or ``--diff-base REF``
    (two-dot ``REF..HEAD``, a plain tree comparison that needs no shared history)."""

    def __init__(self, cfg: Config, staged: bool = False, base: str | None = None) -> None:
        if staged and base:
            raise DiffError("--staged and --diff-base are mutually exclusive")
        if not staged and not base:
            raise DiffError("diff mode needs --staged or --diff-base REF")
        self.cfg = cfg
        self.staged = staged
        self.base = base
        self._changed: set[str] | None = None
        self._prefix: str | None = None
        if base:
            r = run_cmd(["git", "-C", str(cfg.root), "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"], cfg.root)
            if r.returncode:
                raise DiffError(f"--diff-base {base!r} is not a commit this repo can resolve")

    @property
    def ref(self) -> str:
        return "HEAD" if self.staged else str(self.base)

    def _range(self) -> list[str]:
        return ["--cached"] if self.staged else [f"{self.base}..HEAD"]

    def _git(self, *args: str) -> str:
        r = run_cmd(["git", "-C", str(self.cfg.root), *args], self.cfg.root)
        if r.returncode:
            raise DiffError(f"git {' '.join(args[:2])} failed: {r.stderr.strip()[-300:]}")
        return r.stdout

    @property
    def prefix(self) -> str:
        if self._prefix is None:
            self._prefix = self._git("rev-parse", "--show-prefix").strip()
        return self._prefix

    @property
    def changed_files(self) -> set[str]:
        if self._changed is None:
            out = self._git("diff", "--name-only", "--relative", *self._range())
            self._changed = {ln.strip() for ln in out.splitlines() if ln.strip()}
        return self._changed

    def added_lines(self, rel: str) -> set[str]:
        out = self._git("diff", "-U0", *self._range(), "--", rel)
        return {ln[1:] for ln in out.splitlines() if ln.startswith("+") and not ln.startswith("+++")}

    def text_at_base(self, rel: str) -> str | None:
        r = run_cmd(["git", "-C", str(self.cfg.root), "show", f"{self.ref}:{self.prefix}{rel}"], self.cfg.root)
        return None if r.returncode else r.stdout


def scan_at(cfg: Config, current: DocSet, diff: Diff) -> DocSet:
    """The doc set as it was at the diff's base ref (files missing there are skipped)."""
    text = {}
    for f in current.files:
        t = diff.text_at_base(f)
        if t is not None:
            text[f] = t
    return scan(cfg, files=sorted(text), text=text)


# -- markdown structure helpers shared by section checks --------------------------------------------


@dataclass
class Section:
    title: str
    level: int
    heading_line: int
    body: str  # lines after the heading, up to the next heading of the same or higher level


def norm_heading(s: str) -> str:
    s = COMMENT_RX.sub("", s)
    return re.sub(r"\s+", " ", s.lstrip("#").strip()).lower()


def sections(text: str) -> list[Section]:
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in HEADING_RX.finditer(text)]
    out: list[Section] = []
    for i, (pos, level, title) in enumerate(heads):
        body_start = text.find("\n", pos)
        body_start = len(text) if body_start < 0 else body_start + 1
        end = len(text)
        for pos2, level2, _ in heads[i + 1:]:
            if level2 <= level:
                end = pos2
                break
        out.append(Section(title, level, line_of(text, pos), text[body_start:end]))
    return out
