from __future__ import annotations

import json
from pathlib import Path

TABLE_TOML = """
[[registries]]
name = "bugs"
kind = "table"
source = "docs/bug_registry.json"
output = "docs/generated/BUG_REGISTRY.md"
runner = ["runner"]
columns = [["ID", "id"], ["Severity", "severity"], ["Status", "status"], ["Summary", "summary"]]
"""


def _rows(root: Path, rows: list[dict]) -> None:
    (root / "docs/bug_registry.json").write_text(json.dumps({"rows": rows}))


def test_statuses_pass_fail_decision_deferred_broken_and_write_then_check(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=TABLE_TOML)
    _rows(root, [
        {"id": "BUG-001", "summary": "a", "regression_test": "t_pass"},
        {"id": "BUG-002", "summary": "b", "regression_test": "t_fail"},
        {"id": "BUG-003", "summary": "c", "decision_ref": "ADR-0001"},
        {"id": "BUG-004", "summary": "d", "deferred": True, "last_run": "2026-09-01"},
        {"id": "BUG-005", "summary": "e"},
        {"id": "BUG-006", "summary": "f", "regression_test": "t_explode"},
        {"id": "bad id", "summary": "g"},
        {"id": "BUG-001", "summary": "dup"},
    ])
    fake_proc.on(lambda a: a == ["runner", "t_pass"], returncode=0)
    fake_proc.on(lambda a: a == ["runner", "t_fail"], returncode=1)
    fake_proc.on(lambda a: a == ["runner", "t_explode"], returncode=5, stderr="ImportError")
    code, out, _err = run("check")
    assert code == 1
    assert "DG-REGISTRY-MISSING" in out
    assert "DG-REGISTRY-DUP: BUG-001 appears 2 times" in out
    assert "BUG-005: needs a test, a decision_ref, or deferred+last_run" in out
    assert "BUG-006: cited test 't_explode' exited 5" in out
    assert "malformed id 'bad id'" in out

    _rows(root, [
        {"id": "BUG-001", "summary": "a", "regression_test": "t_pass"},
        {"id": "BUG-002", "summary": "b", "regression_test": "t_fail"},
        {"id": "BUG-003", "summary": "c", "decision_ref": "ADR-0001"},
        {"id": "BUG-004", "summary": "d", "deferred": True, "last_run": "2026-09-01"},
    ])
    code, out, _err = run("write", "bugs")
    assert code == 0, out
    md = (root / "docs/generated/BUG_REGISTRY.md").read_text()
    assert "| BUG-001 | - | Fixed | a |" in md
    assert "| BUG-002 | - | Confirmed-Open | b |" in md
    assert "| BUG-003 | - | WontFix | c |" in md
    assert "| BUG-004 | - | Deferred, last run 2026-09-01 | d |" in md
    code, out, _err = run("check")
    assert code == 0, out
    (root / "docs/generated/BUG_REGISTRY.md").write_text(md + "hand edit\n")
    code, out, _err = run("check")
    assert code == 1 and "DG-REGISTRY-STALE" in out


def test_cvss_severity_computed_or_skipped(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n"}, extra_toml=TABLE_TOML)
    _rows(root, [{"id": "TYP-01", "summary": "a", "decision_ref": "ADR-0001", "cvss_vector": "CVSS:4.0/AV:N"}])
    fake_proc.on(lambda a: a[0] == "python3", stdout="High\n")
    code, out, _err = run("write", "bugs")
    assert code == 0, out
    assert "| TYP-01 | High | WontFix | a |" in (root / "docs/generated/BUG_REGISTRY.md").read_text()


def test_location_rot_is_a_row_finding(project, run, fake_proc) -> None:
    root = project({"docs/SPEC.md": "x\n", "src/a.py": "def real(): pass\n"}, extra_toml=TABLE_TOML)
    _rows(root, [{"id": "BUG-001", "summary": "a", "decision_ref": "ADR-0001",
                  "locations": ["src/a.py:real", "src/a.py:gone", "src/missing.py"]}])
    code, out, _err = run("check")
    assert "location 'src/a.py:gone' symbol not found" in out
    assert "location 'src/missing.py' file not found" in out
    assert "src/a.py:real" not in out
