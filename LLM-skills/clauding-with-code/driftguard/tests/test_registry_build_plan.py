from __future__ import annotations

import json
from pathlib import Path

import pytest

from driftguard.registry import is_ledger_title_for

PLAN_TOML = """
[[registries]]
name = "build_plan"
kind = "build_plan"
source = "docs/build_plan.json"
output = "docs/generated/BUILD_PLAN.md"
slice_by = "{slice_by}"
runner = ["runner"]
strict_coverage = {strict}
require_tier2 = {tier2}
"""


def _toml(slice_by: str = "phase", strict: bool = False, tier2: bool = False) -> str:
    return PLAN_TOML.format(slice_by=slice_by, strict=str(strict).lower(), tier2=str(tier2).lower())


def _plan(root: Path, steps: list[dict], tier2: dict | None = None, phases: int = 1) -> None:
    ph = [{"number": i, "title": f"P{i}", "steps": [s for s in steps if s.get("phase", 0) == i]} for i in range(phases)]
    if tier2 is not None:
        for p in ph:
            p["tier2"] = tier2
    (root / "docs/build_plan.json").write_text(json.dumps({"phases": ph, "variance_log": []}))


@pytest.mark.parametrize("step,merged,expected", [
    ({"id": "BP-001", "cancelled": True, "decision_ref": "ADR-0001"}, {"BP-001"}, "cancelled"),
    ({"id": "BP-001", "decision_ref": "ADR-0001", "blocked_on": "x"}, {"BP-001"}, "parked"),
    ({"id": "BP-001", "decision_ref": "no decision"}, set(), "parked"),
    ({"id": "BP-001", "blocked_on": "other team"}, {"BP-001"}, "blocked"),
    ({"id": "BP-001", "verify_test": "t_explode"}, {"BP-001"}, "BROKEN ROW"),
    ({"id": "BP-001", "partial_note": "scope 1/N"}, {"BP-001"}, "partial"),
    ({"id": "BP-001", "umbrella_placeholder": True}, {"BP-001"}, "open"),
    ({"id": "BP-001", "verify_test": "t_pass"}, {"BP-001"}, "shipped"),
    ({"id": "BP-001", "verify_test": "t_fail"}, {"BP-001"}, "open"),
    ({"id": "BP-001"}, set(), "open"),
])
def test_status_precedence(project, run, fake_proc, step, merged, expected) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=_toml("none"))
    _plan(root, [{**step, "title": "T"}])
    fake_proc.gh_titles("merged", [f"feat: {b} done" for b in merged])
    fake_proc.on(lambda a: a == ["runner", "t_pass"], returncode=0)
    fake_proc.on(lambda a: a == ["runner", "t_fail"], returncode=1)
    fake_proc.on(lambda a: a == ["runner", "t_explode"], returncode=7)
    run("write", "build_plan")
    md = (root / "docs/generated/BUILD_PLAN.md").read_text()
    assert f"- **Status:** {expected}" in md, md


def test_ledger_title_proximity() -> None:
    assert is_ledger_title_for("BP-450", "claim BP-450")
    assert is_ledger_title_for("BP-443", "docs(ledger): drop stale BP-442 claim, claim BP-443")
    assert not is_ledger_title_for("BP-384", "feat(audits): BP-384 -- wordlist audit, corrects a stale gap-analysis claim")
    assert not is_ledger_title_for("BP-289", "feat(browser): BP-289/BP-290, JWT claim-PII + reverse-tabnabbing checks")


def test_slices_by_phase_index_links_and_prune(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=_toml("phase"))
    _plan(root, [{"id": "BP-001", "title": "A", "phase": 0, "body_md": "- **Context:** first"},
                 {"id": "BP-002", "title": "B", "phase": 1}], phases=2)
    fake_proc.gh_titles("merged", [])
    code, out, _err = run("write", "build_plan")
    assert code == 0, out
    index = (root / "docs/generated/BUILD_PLAN.md").read_text()
    assert "| BP-001 | open | A | [phase-00](BUILD_PLAN/phase-00.md) |" in index
    p0 = (root / "docs/generated/BUILD_PLAN/phase-00.md").read_text()
    assert "**BP-001 (Phase 0) — A.**" in p0 and "- **Context:** first" in p0
    assert (root / "docs/generated/BUILD_PLAN/phase-01.md").exists()
    code, out, _err = run("check")
    assert code == 0, out
    # drop phase 1 from the source: the orphan guard refuses, until the stale slice is reconciled
    _plan(root, [{"id": "BP-001", "title": "A", "phase": 0}], phases=1)
    code, out, _err = run("write", "build_plan")
    assert code == 1 and "DG-REGISTRY-ORPHAN: BP-002" in out
    (root / "docs/generated/BUILD_PLAN/phase-01.md").unlink()
    code, out, _err = run("write", "build_plan")
    assert code == 0, out
    assert not (root / "docs/generated/BUILD_PLAN/phase-01.md").exists()


def test_slice_by_status_and_none(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=_toml("status"))
    _plan(root, [{"id": "BP-001", "title": "A"}, {"id": "BP-002", "title": "B", "blocked_on": "x"}])
    fake_proc.gh_titles("merged", [])
    assert run("write", "build_plan")[0] == 0
    assert (root / "docs/generated/BUILD_PLAN/open.md").exists()
    assert (root / "docs/generated/BUILD_PLAN/blocked.md").exists()
    (root / "driftguard.toml").write_text((root / "driftguard.toml").read_text().replace('slice_by = "status"', 'slice_by = "none"'))
    assert run("write", "build_plan")[0] == 0
    single = (root / "docs/generated/BUILD_PLAN.md").read_text()
    assert "**BP-001 (Phase 0) — A.**" in single and "**BP-002 (Phase 0) — B.**" in single
    assert list((root / "docs/generated/BUILD_PLAN").glob("*.md")) == []  # stale slices pruned on write


def test_tier2_required_and_undecided_body(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=_toml("none", tier2=True))
    _plan(root, [{"id": "BP-001", "title": "A", "body_md": "- **Do:** pick typer or click, TBD"}],
          tier2={"security": "BP-001", "compatibility": "ADR-0002", "regression": "", "interoperability": None})
    fake_proc.gh_titles("merged", [])
    code, out, _err = run("check")
    assert "phase 0: tier2.regression is empty" in out
    assert "phase 0: tier2.interoperability is empty" in out
    assert "BP-001: body says TBD/undecided with no decision_ref" in out


def test_strict_coverage_undischarged_deferred_and_dangling_discharge(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": """
        **REQ-001 (Ubiquitous).** The system shall exist.
        **REQ-002 (Ubiquitous).** The system shall wait. <!-- deferred: v2 -->
        **REQ-003 (Ubiquitous).** The system shall be forgotten.
        """}, extra_toml=_toml("none", strict=True))
    _plan(root, [{"id": "BP-001", "title": "A", "discharges": ["REQ-001", "REQ-777"]}])
    fake_proc.gh_titles("merged", [])
    code, out, _err = run("check")
    assert "docs/SPEC.md:3: DG-UNDISCHARGED: REQ-003" in out
    assert "REQ-002" not in out
    assert "DG-DANGLING: discharges cites REQ-777" in out
