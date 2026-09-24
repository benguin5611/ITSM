"""Generated registries: a JSON source is the only thing a human edits; the markdown view is
rendered from it, and every field that can be computed (a status from a cited test's exit code,
a severity from a CVSS vector, a step's status from a merged PR) is computed, never hand-typed.
A committed view that differs from the render is a finding."""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

from . import Context, Finding
from . import scan as scanmod

BP_HEADING_RX = re.compile(r"(?m)^\*\*([A-Z]+-\d+) \(Phase \d+\) — ")
LEDGER_WORD_RX = re.compile(r"\b(claims?|releases?d?)\b(?!-)", re.I)
TIER2_KEYS = ("security", "compatibility", "regression", "interoperability")


def render_table_md(title: str, banner: list[str], columns: list[list[str]], rows: list[dict]) -> str:
    lines = [f"# {title} (generated)", "", *banner, "",
             "| " + " | ".join(h for h, _ in columns) + " |",
             "| " + " | ".join("---" for _ in columns) + " |"]
    for r in rows:
        cells = []
        for _, key in columns:
            v = r.get(key)
            if isinstance(v, list):
                v = "; ".join(str(x) for x in v)
            cells.append(str(v) if v not in (None, "", []) else "-")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def run_cited_test(ctx: Context, runner: list[str], test_id: str, pass_code: int, fail_code: int,
                   pass_label: str, fail_label: str) -> tuple[str | None, str | None]:
    """Exactly two exit codes mean anything; anything else is a broken citation."""
    try:
        r = scanmod.run_cmd([*runner, test_id], ctx.cfg.root, timeout=300)
    except Exception as e:  # noqa: BLE001
        return None, f"could not run cited test {test_id!r} ({e})"
    if r.returncode == pass_code:
        return pass_label, None
    if r.returncode == fail_code:
        return fail_label, None
    return None, (f"cited test {test_id!r} exited {r.returncode} (expected {pass_code}={pass_label} or "
                  f"{fail_code}={fail_label}); renamed, deleted or broken? {r.stderr.strip()[-200:]}")


def cvss_severity(ctx: Context, vector: str) -> tuple[str | None, str | None]:
    try:
        r = scanmod.run_cmd(["python3", "-c", "import sys\nfrom cvss import CVSS4\nprint(CVSS4(sys.argv[1]).severity)", vector],
                            ctx.cfg.root, timeout=20)
    except Exception as e:  # noqa: BLE001
        return None, f"cvss package unavailable ({e})"
    if r.returncode:
        return None, (r.stderr.strip().splitlines() or ["unknown error"])[-1][:200]
    return r.stdout.strip(), None


def finalize(ctx: Context, reg: dict, rendered: dict[str, str], write: bool,
             prune_dir: str | None = None) -> list[Finding]:
    """rendered = {relative output path: content}. In check mode, compare with what is committed;
    in write mode, write every output and (for a sliced registry) remove slices no longer rendered."""
    out = []
    src = reg.get("source") or ctx.cfg.rel(ctx.cfg.path)
    if write:
        for rel, content in rendered.items():
            p = ctx.cfg.abs(rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        if prune_dir:
            d = ctx.cfg.abs(prune_dir)
            if d.is_dir():
                keep = {ctx.cfg.abs(r) for r in rendered}
                for stale in d.glob("*.md"):
                    if stale.resolve() not in keep:
                        stale.unlink()
        return out
    for rel, content in rendered.items():
        p = ctx.cfg.abs(rel)
        if not p.exists():
            out.append(Finding(src, 0, "DG-REGISTRY-MISSING", f"{rel} missing; run `driftguard write {reg['name']}`"))
        elif p.read_text(encoding="utf-8") != content:
            out.append(Finding(rel, 0, "DG-REGISTRY-STALE", f"differs from what {src} renders; run `driftguard write {reg['name']}`"))
    return out


def _load_source(ctx: Context, reg: dict) -> tuple[object | None, list[Finding]]:
    p = ctx.cfg.abs(reg["source"])
    if not p.is_file():
        return None, [Finding(reg["source"], 0, "DG-REGISTRY-MISSING", "source file not found")]
    try:
        return json.loads(p.read_text(encoding="utf-8")), []
    except ValueError as e:
        return None, [Finding(reg["source"], 0, "DG-REGISTRY-ROW", f"source is not valid JSON: {e}")]


def _location_findings(ctx: Context, src: str, ident: str, locations: list[str]) -> list[Finding]:
    out = []
    for loc in locations:
        path, _, symbol = loc.partition(":")
        p = ctx.cfg.abs(path)
        if not p.is_file():
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: location {loc!r} file not found"))
            continue
        if symbol and not re.search(rf"\b{re.escape(symbol)}\b", p.read_text(encoding="utf-8", errors="replace")):
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: location {loc!r} symbol not found"))
    return out


# -- kind = table ------------------------------------------------------------------------------------------


def table_registry(ctx: Context, reg: dict, write: bool) -> list[Finding]:
    data, out = _load_source(ctx, reg)
    if data is None:
        return out
    rows = data.get("rows", data) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        return [Finding(reg["source"], 0, "DG-REGISTRY-ROW", "expected a list of rows (or {rows: [...]})")]
    labels = reg["status_labels"]
    src = reg["source"]
    seen = collections.Counter(r.get("id", "") for r in rows)
    for ident, n in seen.items():
        if n > 1:
            out.append(Finding(src, 0, "DG-REGISTRY-DUP", f"{ident} appears {n} times"))
    rendered_rows = []
    cvss_unavailable = False
    for r in rows:
        ident = str(r.get("id", ""))
        if not reg["id_pattern"].match(ident):
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"malformed id {ident!r}"))
            continue
        row = dict(r)
        if r.get("locations"):
            out += _location_findings(ctx, src, ident, r["locations"])
        vector = r.get("cvss_vector")
        if vector and not cvss_unavailable:
            sev, err = cvss_severity(ctx, vector)
            if err and sev is None and "unavailable" in err:
                cvss_unavailable = True
                ctx.skipped.append(f"{reg['name']}: severity not computed ({err})")
                row["severity"] = "-"
            elif err:
                out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: malformed CVSS vector: {err}"))
                row["severity"] = "BROKEN"
            else:
                row["severity"] = sev
        elif vector:
            row["severity"] = "-"
        test_id = r.get("regression_test") or r.get("test")
        if r.get("deferred"):
            if not r.get("last_run"):
                out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: deferred without last_run"))
                row["status"] = "BROKEN ROW"
            else:
                row["status"] = f"Deferred, last run {r['last_run']}"
        elif test_id:
            status, err = run_cited_test(ctx, reg["runner"], test_id, reg["pass_code"], reg["fail_code"],
                                         labels["pass"], labels["fail"])
            if err:
                out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: {err}"))
                status = "BROKEN ROW"
            row["status"] = status
        elif r.get("decision_ref"):
            row["status"] = labels["decision"]
        else:
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{ident}: needs a test, a decision_ref, or deferred+last_run"))
            row["status"] = "BROKEN ROW"
        rendered_rows.append(row)
    columns = reg["columns"] or [["ID", "id"], ["Status", "status"], ["Summary", "summary"],
                                 ["Test", "regression_test"], ["Decision", "decision_ref"]]
    banner = [f"*Generated from `{src}` — do not hand-edit. Status is computed from each row's cited test "
              f"(pass → `{labels['pass']}`, expected-fail → `{labels['fail']}`), a decision_ref → `{labels['decision']}`, "
              "or deferred+last_run; never hand-typed. Regenerate with `driftguard write "
              f"{reg['name']}`.*"]
    rendered = render_table_md(reg["title"] or reg["name"].replace("_", " ").title(), banner, columns, rendered_rows)
    out += finalize(ctx, reg, {reg["output"]: rendered}, write)
    return out


# -- kind = id_register ------------------------------------------------------------------------------------


def id_register(ctx: Context, reg: dict, write: bool) -> list[Finding]:
    ds = ctx.docs
    lines = [f"# {reg['title'] or 'Identifier register'} (generated)", "",
             "*Generated from the doc set — do not hand-edit. IDs are stable, non-positional and tombstoned on "
             f"removal. Regenerate with `driftguard write {reg['name']}`.*", ""]
    for ic in ctx.cfg.id_classes:
        ids = ds.all_ids(ic.name)
        lines += [f"## {ic.name} ({len(ids)})", ""]
        if not ids:
            lines += ["none", ""]
            continue
        lines += ["| ID | Title | Home |", "| --- | --- | --- |"]
        for ident in ids:
            home = ds.def_sites[ident][0][0]
            tomb = " (tombstoned)" if ident in ds.tombstones else ""
            lines.append(f"| `{ident}`{tomb} | {ds.titles.get(ident) or '-'} | {home} |")
        lines.append("")
    if reg["backlinks"]:
        lines += ["## Referenced from", "", "| ID | Files |", "| --- | --- |"]
        for ident in sorted(ds.cls_of):
            refs = ds.referenced_from(ident)
            if refs:
                lines.append(f"| `{ident}` | {', '.join(refs)} |")
        lines.append("")
    tomb = ", ".join(f"`{t}`" for t in sorted(ds.tombstones)) or "none"
    lines += [f"Tombstoned: {tomb}.", ""]
    return finalize(ctx, reg, {reg["output"]: "\n".join(lines)}, write)


# -- kind = build_plan ----------------------------------------------------------------------------------------


def is_ledger_title_for(ident: str, title: str) -> bool:
    """A claims/release housekeeping PR carries the bare ID too; match by proximity, not by
    the word appearing anywhere in the title."""
    for m in re.finditer(rf"\b{re.escape(ident)}\b", title):
        window = title[max(0, m.start() - 24): m.end() + 24]
        if LEDGER_WORD_RX.search(window):
            return True
    return False


def _merged_ids(ctx: Context, candidates: list[str]) -> set[str]:
    if not candidates:
        return set()
    try:
        r = scanmod.run_cmd(["gh", "pr", "list", "--state", "merged", "--limit", "100000", "--json", "title"],
                            ctx.cfg.root, timeout=60)
    except Exception as e:  # noqa: BLE001
        ctx.skipped.append(f"build_plan: merged-PR check skipped (gh unreachable: {e})")
        return set()
    if r.returncode:
        ctx.skipped.append(f"build_plan: merged-PR check skipped (gh exited {r.returncode})")
        return set()
    titles = [pr["title"] for pr in json.loads(r.stdout or "[]")]
    return {b for b in candidates if any(re.search(rf"\b{re.escape(b)}\b", t) and not is_ledger_title_for(b, t) for t in titles)}


def compute_step(ctx: Context, reg: dict, step: dict, merged: set[str]) -> tuple[str, list[Finding]]:
    src = reg["source"]
    bid = step.get("id", "?")
    out = []
    for p in step.get("do_touches") or []:
        if not ctx.cfg.abs(p).exists():
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{bid}: do_touches path not found: {p!r}"))
    verified: bool | None = True
    vt = step.get("verify_test")
    if vt:
        label, err = run_cited_test(ctx, reg["runner"], vt, reg["pass_code"], reg["fail_code"], "Verified", "Not-Verified")
        if err:
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{bid}: {err}"))
            verified = None
        else:
            verified = label == "Verified"
            if not verified:
                out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{bid}: cited verify_test {vt!r} currently fails"))
    decision = step.get("decision_ref")
    if step.get("cancelled"):
        status = "cancelled"
    elif decision:
        if not re.match(r"[A-Z]+-\d+$", str(decision)) and str(decision).strip().lower() != "no decision":
            out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{bid}: decision_ref {decision!r} is neither an ID nor 'no decision'"))
        status = "parked"
    elif step.get("blocked_on"):
        status = "blocked"
    elif verified is None:
        status = "BROKEN ROW"
    elif step.get("partial_note"):
        status = "partial"
    elif step.get("umbrella_placeholder"):
        status = "open"
    elif verified and bid in merged:
        status = "shipped"
    else:
        status = "open"
    body = step.get("body_md") or ""
    if re.search(r"(?i)\b(TBD|undecided)\b", body) and not decision and status != "cancelled":
        out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"{bid}: body says TBD/undecided with no decision_ref — that is a fork for the human, not a default"))
    return status, out


def _banner(reg: dict) -> list[str]:
    return [f"*Generated from `{reg['source']}` — do not hand-edit. `Status` is computed, never hand-typed: "
            "`shipped` needs a merged PR naming the step and (if set) a passing `verify_test`; `parked`, `blocked`, "
            "`cancelled` and `partial` come from the step's own fields. Everything below `Status` is the step's "
            f"`body_md`, verbatim. Regenerate with `driftguard write {reg['name']}`.*"]


def _step_block(phase: dict, step: dict, status: str) -> list[str]:
    bid = step["id"]
    lines = [f"**{bid} (Phase {phase['number']}) — {step.get('title', '')}.**", "", f"- **Status:** {status}"]
    if step.get("verify_test"):
        lines.append(f"- **Verify test:** `{step['verify_test']}`")
    if step.get("do_touches"):
        lines.append(f"- **Do touches:** {', '.join(step['do_touches'])}")
    if step.get("discharges"):
        lines.append(f"- **Discharges:** {', '.join(step['discharges'])}")
    if step.get("body_md"):
        lines.append(step["body_md"].rstrip("\n"))
    lines.append("")
    return lines


def slice_dir(reg: dict) -> str:
    """`docs/generated/BUILD_PLAN.md` → `docs/generated/BUILD_PLAN` (slices live beside the index)."""
    return Path(reg["output"]).with_suffix("").as_posix()


def _render_build_plan(cfg: dict, reg: dict, computed: dict[str, str]) -> dict[str, str]:
    out_rel = reg["output"]
    stem = Path(out_rel).stem
    slice_by = reg["slice_by"]
    phases = cfg.get("phases") or []
    index = [f"# Build plan (generated)", "", *_banner(reg), ""]
    for rule in cfg.get("build_rules") or []:
        index.append(f"- **{rule['id']}** {rule['text']}")
    if cfg.get("build_rules"):
        index.append("")
    files: dict[str, list[str]] = {}
    counts = collections.Counter(computed.values())
    if slice_by != "none":
        index += ["Status: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ".", ""]
    for phase in phases:
        index += [f"## Phase {phase['number']} — {phase.get('title', '')}", ""]
        if phase.get("phase_intro"):
            index += [phase["phase_intro"], ""]
        if slice_by == "none":
            for step in phase.get("steps") or []:
                index += _step_block(phase, step, computed[step["id"]])
            continue
        tier2 = phase.get("tier2") or {}
        if tier2:
            index += ["Tier 2: " + ", ".join(f"{k} → {tier2.get(k) or '-'}" for k in TIER2_KEYS), ""]
        index += ["| ID | Status | Title | Where |", "| --- | --- | --- | --- |"]
        for step in phase.get("steps") or []:
            status = computed[step["id"]]
            slice_name = f"phase-{int(phase['number']):02d}" if slice_by == "phase" else status.lower().replace(" ", "-")
            rel = f"{slice_dir(reg)}/{slice_name}.md"
            index.append(f"| {step['id']} | {status} | {step.get('title', '')} | [{slice_name}]({stem}/{slice_name}.md) |")
            block = files.setdefault(rel, [f"# {'Phase ' + str(phase['number']) + ' — ' + phase.get('title', '') if slice_by == 'phase' else status} (generated)", "", *_banner(reg), ""])
            block += _step_block(phase, step, status)
        index.append("")
    index += ["## Variance log", "", "| Date | Plan said | Reality | Resolution |", "| --- | --- | --- | --- |"]
    for v in cfg.get("variance_log") or []:
        index.append(f"| {v.get('date', '-')} | {v.get('plan_said', '-')} | {v.get('reality', '-')} | {v.get('resolution', '-')} |")
    rendered = {out_rel: "\n".join(index) + "\n"}
    for rel, lines in files.items():
        rendered[rel] = "\n".join(lines) + "\n"
    return rendered


def _committed_step_ids(ctx: Context, reg: dict) -> set[str]:
    ids = set()
    paths = [ctx.cfg.abs(reg["output"])]
    sdir = ctx.cfg.abs(slice_dir(reg))
    if sdir.is_dir():
        paths += sorted(sdir.glob("*.md"))
    for p in paths:
        if p.is_file():
            ids |= {m.group(1) for m in BP_HEADING_RX.finditer(p.read_text(encoding="utf-8", errors="replace"))}
    return ids


def build_plan(ctx: Context, reg: dict, write: bool) -> list[Finding]:
    cfg, out = _load_source(ctx, reg)
    if cfg is None:
        return out
    src = reg["source"]
    phases = cfg.get("phases") or []
    steps = [s for ph in phases for s in ph.get("steps") or []]
    for bid, n in collections.Counter(s.get("id") for s in steps).items():
        if n > 1:
            out.append(Finding(src, 0, "DG-REGISTRY-DUP", f"{bid} appears {n} times"))
    orphaned = sorted(_committed_step_ids(ctx, reg) - {s.get("id") for s in steps})
    for bid in orphaned:
        out.append(Finding(src, 0, "DG-REGISTRY-ORPHAN",
                           f"{bid} is rendered in the committed output but absent from the source; a merge lost it. "
                           "Reconstruct the step in the source before regenerating."))
    if orphaned:
        return out  # never write from a source known to be missing content
    if reg["require_tier2"]:
        for ph in phases:
            tier2 = ph.get("tier2") or {}
            for key in TIER2_KEYS:
                if not tier2.get(key):
                    out.append(Finding(src, 0, "DG-REGISTRY-ROW", f"phase {ph.get('number')}: tier2.{key} is empty (name a step ID or a decision ID)"))
    merged = _merged_ids(ctx, [s["id"] for s in steps if not s.get("cancelled")])
    computed = {}
    for ph in phases:
        for step in ph.get("steps") or []:
            status, problems = compute_step(ctx, reg, step, merged)
            computed[step["id"]] = status
            out += problems
    if reg["strict_coverage"]:
        cls = reg["discharges_class"]
        discharged = {d for s in steps for d in (s.get("discharges") or [])}
        for d in sorted(discharged):
            if ctx.docs.cls_of.get(d) != cls:
                out.append(Finding(src, 0, "DG-DANGLING", f"discharges cites {d}, which is not a defined {cls}"))
        for ident in ctx.docs.all_ids(cls):
            if ident in discharged or ident in ctx.docs.tombstones:
                continue
            path, ln = ctx.docs.def_sites[ident][0]
            line = ctx.docs.text[path].split("\n")[ln - 1]
            if "<!-- deferred:" in line:
                continue
            out.append(Finding(path, ln, "DG-UNDISCHARGED", f"{ident} is discharged by no step and not marked `<!-- deferred: reason -->`"))
    out += finalize(ctx, reg, _render_build_plan(cfg, reg, computed), write, prune_dir=slice_dir(reg))
    return out


KINDS = {"table": table_registry, "id_register": id_register, "build_plan": build_plan}


def run_registries(ctx: Context, write_name: str | None = None) -> list[Finding]:
    out = []
    for reg in ctx.cfg.registries:
        if write_name is not None and reg["name"] != write_name:
            continue
        out += KINDS[reg["kind"]](ctx, reg, write=write_name is not None)
    return out
