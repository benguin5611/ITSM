"""One function per CHECK-ID. Each takes a Context and returns findings. ``BUILTIN`` lists the
checks the CLI runs; a plugin module adds its own via ``CHECKS``."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from . import Context, Finding
from . import scan as scanmod
from .scan import COMMENT_RX, norm_heading, sections

EARS_RX = re.compile(
    r"^(The system shall\b"
    r"|When\b.+?,\s*the system shall\b"
    r"|While\b.+?,\s*the system shall\b"
    r"|Where\b.+?,\s*the system shall\b"
    r"|If\b.+?,\s*then\b.*?the system shall\b)",
    re.S,
)
PLACEHOLDER_RX = re.compile(r"<[^<>\n]{1,80}>")
TABLE_SEP_RX = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
COMMENTISH_RX = re.compile(r"(#|//|/\*|\*|--)\s|[\"']")
SEGMENT_RX = re.compile(r"(?<=[.!?])\s+|\s+--\s+|\s+—\s+")
BAD_CELLS = {"", "-", "tbd", "todo", "?"}


def _lines(text: str) -> list[str]:
    return text.split("\n")


# -- always-on, from the scan ------------------------------------------------------------------------


def check_dangling(ctx: Context) -> list[Finding]:
    out = []
    for cls, ids in ctx.docs.refs.items():
        for ident, sites in ids.items():
            if ident in ctx.docs.defs.get(cls, {}):
                continue
            for path, ln in sites:
                out.append(Finding(path, ln, "DG-DANGLING", f"{ident} is referenced but never defined"))
    return out


def check_duplicate(ctx: Context) -> list[Finding]:
    out = []
    for cls, counter in ctx.docs.defs.items():
        for ident, n in counter.items():
            if n > 1:
                sites = ctx.docs.def_sites[ident]
                path, ln = sites[0]
                others = ", ".join(f"{p}:{l}" for p, l in sites[1:])
                out.append(Finding(path, ln, "DG-DUPLICATE", f"{ident} defined {n} times (also at {others})"))
    return out


def check_tombstone(ctx: Context) -> list[Finding]:
    out = []
    markers = ctx.cfg.supersede_markers
    for ident in sorted(ctx.docs.tombstones):
        cls_name = ctx.docs.cls_of.get(ident)
        ic = ctx.cfg.class_named(cls_name) if cls_name else None
        per_file = bool(ic and (ic.def_files or ic.filename_must_match))
        own_sites = set(ctx.docs.def_sites.get(ident, []))
        own_files = {p for p, _ in own_sites}
        rx = re.compile(rf"(?<![\w-]){re.escape(ident)}(?![\w-])")
        for path, text in ctx.docs.text.items():
            if (per_file and path in own_files) or ctx.cfg.is_generated(path):
                continue
            for i, line in enumerate(_lines(text), 1):
                if (path, i) in own_sites or not rx.search(line):
                    continue
                if any(mk in line for mk in markers):
                    continue
                out.append(Finding(path, i, "DG-TOMBSTONE",
                                   f"{ident} is superseded/removed but cited here as if active"))
    return out


def check_scan_findings(ctx: Context) -> list[Finding]:
    """DG-LEGACY and DG-FILENAME are produced during the scan itself."""
    return list(ctx.docs.findings)


def check_ears(ctx: Context) -> list[Finding]:
    out = []
    for ic in ctx.cfg.id_classes:
        if not ic.ears:
            continue
        for ident in ctx.docs.all_ids(ic.name):
            for path, ln in ctx.docs.def_sites[ident]:
                line = _lines(ctx.docs.text[path])[ln - 1]
                m = ic.definition.search(line)
                rest = line[m.end():] if m else line
                # `**REQ-001 (Event).** When …` / `**REQ-001 Title.** The system shall …`:
                # the clause starts after the closing bold; otherwise right after the ID.
                if "**" in rest:
                    rest = rest.split("**", 1)[1]
                rest = re.sub(r"^[\s.:—–-]+", "", rest)
                if not EARS_RX.match(rest):
                    out.append(Finding(path, ln, "DG-EARS",
                                       f"{ident} does not open with one of the five EARS shall-clauses"))
    return out


# -- templates: required sections, complete tables, assumptions ---------------------------------------


def _section_empty(body: str) -> str | None:
    """Return a reason if the section body carries no real content, else None."""
    text = COMMENT_RX.sub("", body)
    rows = [ln for ln in _lines(text) if ln.strip()]
    if not rows:
        return "section is empty"
    table = [ln for ln in rows if ln.lstrip().startswith("|")]
    prose = [ln for ln in rows if not ln.lstrip().startswith("|")]
    if table and not prose:
        data = [ln for ln in table if not TABLE_SEP_RX.match(ln.strip())]
        if len(data) <= 1:
            return "table has a header but no rows"
        real = []
        for ln in data[1:]:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            # the first cell is usually a template-supplied label; the row is filled only if a later cell is
            judged = cells[1:] if len(cells) > 1 else cells
            if any(re.search(r"\w", PLACEHOLDER_RX.sub("", c)) for c in judged):
                real.append(ln)
        if not real:
            return "table rows are only placeholders"
        return None
    stripped = PLACEHOLDER_RX.sub("", "\n".join(prose))
    if not re.search(r"\w", stripped):
        return "only placeholders"
    if re.fullmatch(r"\s*(none|n/?a|tbd|todo)\W*\s*", stripped, re.I):
        return "'none' needs a reason"
    return None


def _table_rows(body: str) -> list[tuple[int, list[str]]]:
    rows = []
    for i, ln in enumerate(_lines(body)):
        s = ln.strip()
        if not s.startswith("|") or TABLE_SEP_RX.match(s):
            continue
        rows.append((i, [c.strip() for c in s.strip("|").split("|")]))
    return rows[1:] if rows else []  # drop the header row


def check_sections(ctx: Context) -> list[Finding]:
    out = []
    for rule in ctx.cfg.templates:
        for path in ctx.docs.files:
            if not ctx.cfg.matches(path, rule["match"]):
                continue
            text = ctx.docs.text[path]
            secs = sections(text)
            by_name = {norm_heading(s.title): s for s in secs}
            for req in rule["required"]:
                sec = by_name.get(norm_heading(req))
                if sec is None:
                    out.append(Finding(path, 0, "DG-SECTION", f"required section missing: {req.lstrip('#').strip()!r}"))
                    continue
                why = _section_empty(sec.body)
                if why:
                    out.append(Finding(path, sec.heading_line, "DG-SECTION",
                                       f"required section {req.lstrip('#').strip()!r}: {why}"))
            for heading in rule["complete_tables"]:
                sec = by_name.get(norm_heading(heading))
                if sec is None:
                    continue
                for off, cells in _table_rows(sec.body):
                    if any(PLACEHOLDER_RX.sub("", c).strip().lower() in BAD_CELLS for c in cells[1:]):
                        out.append(Finding(path, sec.heading_line + 1 + off, "DG-ROW-INCOMPLETE",
                                           f"row {cells[0]!r} under {heading.lstrip('#').strip()!r} has an empty cell"))
            heading = rule.get("assumptions_table")
            if heading:
                sec = by_name.get(norm_heading(heading))
                if sec is not None:
                    for off, cells in _table_rows(sec.body):
                        if len(cells) < 3:
                            continue
                        status = cells[1].lower()
                        ln = sec.heading_line + 1 + off
                        if status not in ("verified", "unverified"):
                            out.append(Finding(path, ln, "DG-ASSUMPTION",
                                               f"status must be 'verified' or 'unverified', got {cells[1]!r}"))
                        elif status == "unverified" and "accepted-risk:" not in cells[-1].lower():
                            out.append(Finding(path, ln, "DG-ASSUMPTION",
                                               f"unverified assumption {cells[0]!r} has no 'accepted-risk: <name, date>' sign-off"))
    return out


def check_banned(ctx: Context) -> list[Finding]:
    out = []
    for rule in ctx.cfg.banned:
        for path in ctx.cfg.expand(rule["files"]):
            text = ctx.docs.text.get(path)
            if text is None:
                text = ctx.cfg.read(path)
            for m in rule["pattern"].finditer(text):
                ln = scanmod.line_of(text, m.start())
                line = _lines(text)[ln - 1]
                if any(x.search(line) for x in rule["except"]):
                    continue
                out.append(Finding(path, ln, "DG-BANNED", rule["message"]))
    return out


# -- source-side checks ---------------------------------------------------------------------------------


def check_leaks(ctx: Context) -> list[Finding]:
    if not ctx.cfg.leaks:
        return []
    rx = ctx.cfg.leaks["id_pattern"]
    if rx is None:
        pats = [ic.ref.pattern for ic in ctx.cfg.id_classes]
        if not pats:
            return []
        rx = re.compile("|".join(f"(?:{p})" for p in pats))
    out = []
    for path in ctx.cfg.expand(ctx.cfg.leaks["globs"]):
        if path.endswith(".md"):
            continue
        for i, line in enumerate(_lines(ctx.cfg.read(path)), 1):
            if rx.search(line) and COMMENTISH_RX.search(line):
                out.append(Finding(path, i, "DG-LEAK", "doc-set ID leaked into source (comment or string)"))
    return out


def _enclosing_function(source: str, lineno: int) -> str | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end = node.lineno, getattr(node, "end_lineno", node.lineno)
            if start <= lineno <= end and (best is None or end - start < best[1] - best[0]):
                best = (start, end)
    if best is None:
        return None
    return "\n".join(_lines(source)[best[0] - 1: best[1]])


def check_adoption(ctx: Context) -> list[Finding]:
    out = []
    for rule in ctx.cfg.adoption:
        allow = set(rule["allow_files"])
        for path in ctx.cfg.expand(rule["glob"]):
            if path in allow or Path(path).name in allow:
                continue
            src = ctx.cfg.read(path)
            lines = _lines(src)
            for i, line in enumerate(lines, 1):
                if not rule["pattern"].search(line):
                    continue
                if rule["justification"]:
                    if path.endswith(".py"):
                        body = _enclosing_function(src, i)
                        window = body if body is not None else "\n".join(lines[max(0, i - 4): i])
                    else:
                        window = "\n".join(lines[max(0, i - 4): i])
                    if rule["justification"].search(window):
                        continue
                out.append(Finding(path, i, "DG-ADOPTION", rule["message"]))
    return out


# -- diff-scoped checks --------------------------------------------------------------------------------


def check_currency(ctx: Context) -> list[Finding]:
    if not ctx.cfg.currency or ctx.diff is None:
        return []
    changed = ctx.diff.changed_files
    if not changed:
        return []
    claim, path_rx = ctx.cfg.currency["claim"], ctx.cfg.currency["path"]
    out = []
    for path in ctx.cfg.expand(ctx.cfg.currency["docs"]):
        text = ctx.docs.text.get(path) or ctx.cfg.read(path)
        added = ctx.diff.added_lines(path) if path in changed else set()
        for i, line in enumerate(_lines(text), 1):
            if line in added:
                continue
            for seg in SEGMENT_RX.split(line):
                m = claim.search(seg)
                if not m:
                    continue
                for cited in path_rx.findall(seg):
                    if any(c == cited or c.endswith("/" + cited) for c in changed):
                        out.append(Finding(path, i, "DG-CURRENCY",
                                           f"cites {cited!r} (changed in this diff) with a currency claim ({m.group(0)!r}) but this line was not touched"))
                        break
    return out


def _num(ident: str) -> int:
    return int(re.findall(r"\d+", ident)[-1])


def _family(ident: str) -> str:
    return re.sub(r"\d+$", "", ident)


def _pr_titles(ctx: Context, state: str) -> list[str] | None:
    try:
        r = scanmod.run_cmd(["gh", "pr", "list", "--state", state, "--limit", "1000", "--json", "title"],
                            ctx.cfg.root, timeout=30)
    except Exception as e:  # noqa: BLE001 - any failure is a non-result, reported as skipped
        ctx.skipped.append(f"DG-HWM: gh unreachable ({e})")
        return None
    if r.returncode:
        ctx.skipped.append(f"DG-HWM: gh exited {r.returncode}: {r.stderr.strip()[-200:]}")
        return None
    try:
        return [pr["title"] for pr in json.loads(r.stdout or "[]")]
    except (ValueError, KeyError, TypeError):
        ctx.skipped.append("DG-HWM: gh returned unparseable JSON")
        return None


def check_hwm(ctx: Context) -> list[Finding]:
    classes = [ic for ic in ctx.cfg.id_classes if ic.allocate]
    if not classes:
        return []
    merged = _pr_titles(ctx, "merged")
    if merged is None:
        return []
    cfg_rel = ctx.cfg.rel(ctx.cfg.path)
    out = []
    before = scanmod.scan_at(ctx.cfg, ctx.docs, ctx.diff) if ctx.diff is not None else None
    open_titles = None if before is not None else _pr_titles(ctx, "open")
    for ic in classes:
        local = ctx.docs.all_ids(ic.name)
        pr_ids = {m.group(0) for t in merged for m in ic.ref.finditer(t)}
        families = {_family(i) for i in local} | {_family(i) for i in pr_ids}
        if before is not None:
            prior = set(before.all_ids(ic.name))
            families |= {_family(i) for i in prior}
        for fam in sorted(families):
            local_f = [i for i in local if _family(i) == fam]
            pr_f = [i for i in pr_ids if _family(i) == fam]
            local_max = max((_num(i) for i in local_f), default=0)
            merged_max = max((_num(i) for i in pr_f), default=0)
            if before is not None:
                prior_f = [i for i in before.all_ids(ic.name) if _family(i) == fam]
                floor = max([_num(i) for i in prior_f] + [_num(i) for i in pr_f], default=0)
                for ident in sorted(set(local_f) - set(prior_f), key=_num):
                    if _num(ident) <= floor and ident not in pr_ids:
                        path, ln = ctx.docs.def_sites[ident][0]
                        out.append(Finding(path, ln, "DG-HWM",
                                           f"{ident} is new in this diff but at or below the high-water mark {fam}{floor} (existing docs + merged PR titles); draw a higher number"))
            else:
                if merged_max > local_max:
                    out.append(Finding(cfg_rel, 0, "DG-HWM",
                                       f"a merged PR title spent {fam}{merged_max} but the doc set's max is {fam}{local_max}; do not re-issue a number up to {fam}{merged_max}"))
                if open_titles is not None:
                    open_max = max((_num(m.group(0)) for t in open_titles for m in ic.ref.finditer(t) if _family(m.group(0)) == fam), default=0)
                    if open_max > max(local_max, merged_max):
                        out.append(Finding(cfg_rel, 0, "DG-HWM",
                                           f"an open PR title already claims {fam}{open_max}; re-derive the next free number before allocating"))
    return out


BUILTIN = [
    check_dangling, check_duplicate, check_tombstone, check_scan_findings, check_ears,
    check_sections, check_banned, check_leaks, check_adoption, check_currency, check_hwm,
]
