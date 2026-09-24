from __future__ import annotations

import pytest

GATE_TOML = """
[[templates]]
match = "docs/gate.md"
required = ["## Open forks", "## Declined alternatives", "## Need"]
complete_tables = ["## Prior art"]
assumptions_table = "## Assumptions"
"""


def _codes(out: str) -> list[str]:
    return [ln.split(": ")[1] for ln in out.splitlines() if ": DG-" in ln]


def test_clean_doc_set_exits_zero(project, run) -> None:
    project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n"})
    code, out, _err = run("check")
    assert code == 0 and "clean" in out


def test_dangling_and_duplicate(project, run) -> None:
    project({"docs/SPEC.md": """
        **REQ-001 (Ubiquitous).** The system shall exist. See REQ-009.
        **REQ-001 (Ubiquitous).** The system shall exist twice.
        """})
    code, out, _err = run("check")
    assert code == 1
    assert "docs/SPEC.md:1: DG-DANGLING: REQ-009" in out
    assert "DG-DUPLICATE: REQ-001 defined 2 times" in out


def test_tombstoned_id_cited_as_active_fails_unless_marker_present(project, run) -> None:
    project({
        "docs/decisions/ADR-0001-go.md": "---\nstatus: superseded-by ADR-0002\n---\n# ADR-0001 — Go\n\nADR-0001 is this file; mentioning itself is fine.\n",
        "docs/decisions/ADR-0002-python.md": "# ADR-0002 — Python\n\nADR-0002 supersedes ADR-0001.\n",
        "docs/SPEC.md": "Built per ADR-0001.\n",
    })
    code, out, _err = run("check")
    assert code == 1
    assert "docs/SPEC.md:1: DG-TOMBSTONE: ADR-0001" in out
    assert "ADR-0002-python.md" not in out, out


@pytest.mark.parametrize("clause", [
    "The system shall start.",
    "When the user clicks, the system shall save.",
    "While offline, the system shall queue.",
    "Where a plugin is present, the system shall load it.",
    "If input is malformed, then the system shall reject it.",
])
def test_ears_five_forms_pass(project, run, clause: str) -> None:
    project({"docs/SPEC.md": f"**REQ-001 (Form).** {clause}\n**REQ-002 Title.** {clause}\n"})
    code, out, _err = run("check")
    assert code == 0, out


def test_ears_deviation_fails(project, run) -> None:
    project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** Users can log in.\n"})
    code, out, _err = run("check")
    assert code == 1 and "DG-EARS: REQ-001" in out


def test_required_section_missing_empty_placeholder_and_header_only_table(project, run) -> None:
    project({"docs/gate.md": """
        # Gate

        ## Need
        <!-- one line -->
        <what this makes true>

        ## Open forks
        | Fork | Options | Recommendation | Decision |
        | --- | --- | --- | --- |
        """}, extra_toml=GATE_TOML)
    code, out, _err = run("check")
    assert code == 1
    lines = [ln for ln in out.splitlines() if "DG-SECTION" in ln]
    assert any("'Declined alternatives'" in ln and "missing" in ln for ln in lines)
    assert any("'Need'" in ln and "placeholders" in ln for ln in lines)
    assert any("'Open forks'" in ln and "no rows" in ln for ln in lines)


def test_filled_sections_pass_and_none_needs_a_reason(project, run) -> None:
    root = project({"docs/gate.md": """
        # Gate

        ## Need
        Operators cannot tell which stage failed.

        ## Open forks
        | Fork | Options | Recommendation | Decision |
        | --- | --- | --- | --- |
        | Storage | sqlite / postgres | sqlite | sqlite (Ben, 2026-09-02) |

        ## Declined alternatives
        none
        """}, extra_toml=GATE_TOML)
    code, out, _err = run("check")
    assert code == 1 and "'Declined alternatives': 'none' needs a reason" in out
    (root / "docs/gate.md").write_text((root / "docs/gate.md").read_text().replace("none\n", "none — single obvious option, see Open forks\n"))
    code, out, _err = run("check")
    assert code == 0, out


def test_incomplete_rows_and_assumptions(project, run) -> None:
    project({"docs/gate.md": """
        ## Need
        real

        ## Open forks
        n/a — no forks arose; see Need

        ## Declined alternatives
        none — nothing declined, one option

        ## Prior art
        | Candidate | Verdict | Reason |
        | --- | --- | --- |
        | typer | adopt | fits |
        | click | - | <why not> |

        ## Assumptions
        | Assumption | Status | Check |
        | --- | --- | --- |
        | gh is installed | verified | `gh --version` |
        | CI runner is Linux | unverified | check workflow |
        | Postgres 16 | unverified | accepted-risk: Ben, 2026-09-02 |
        | Redis | maybe | ? |
        """}, extra_toml=GATE_TOML)
    code, out, _err = run("check")
    assert code == 1
    assert "DG-ROW-INCOMPLETE: row 'click'" in out
    assert "DG-ASSUMPTION: unverified assumption 'CI runner is Linux'" in out
    assert "DG-ASSUMPTION: status must be" in out
    assert "Postgres 16" not in out


def test_label_first_table_counts_as_empty_until_a_value_cell_is_filled(project, run) -> None:
    project({"docs/gate.md": """
        ## Need
        real

        ## Open forks
        | Field | Value |
        | --- | --- |
        | system | <tracker or forge> |
        | key prefix | <PROJ-> |

        ## Declined alternatives
        | Field | Value |
        | --- | --- |
        | system | the tracker |
        | key prefix | <PROJ-> |
        """}, extra_toml=GATE_TOML)
    code, out, _err = run("check")
    assert code == 1
    assert "'Open forks': table rows are only placeholders" in out
    assert "Declined alternatives" not in out


def test_banned_pattern_with_exception(project, run) -> None:
    project({"docs/PLAN.md": "## Known Gaps\n\n- foo\n\n## Known Gaps (historical, archived)\n"},
            extra_toml="""
        [[banned]]
        pattern = '(?m)^#{1,3}\\s*Known Gaps\\b'
        message = "every gap is its own step ID, not a list"
        except = ["archived"]
    """)
    code, out, _err = run("check")
    assert code == 1
    assert out.count("DG-BANNED") == 1 and "docs/PLAN.md:1:" in out
