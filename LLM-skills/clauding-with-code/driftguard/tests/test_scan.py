from __future__ import annotations

from driftguard.config import load
from driftguard.scan import scan, sections


def test_defs_refs_titles_across_anchor_styles(project) -> None:
    root = project({
        "docs/SPEC.md": """
            **REQ-001 (Ubiquitous).** The system shall load. See ADR-0001 and BP-001.
            | ID | Invariant |
            | --- | --- |
            | INV-1 | one tool |
            """,
        "docs/decisions/ADR-0001-one-tool.md": """
            ---
            id: ADR-0001
            status: active
            ---
            # ADR-0001 — One tool, not two
            """,
        "docs/generated/BUILD_PLAN/phase-00.md": "**BP-001 (Phase 0) — Skeleton.**\n\n- **Status:** open\n",
    }, extra_toml="""
        [[id_classes]]
        name = "INV"
        ref = '\\bINV-\\d+\\b'
        def = '(?m)^\\|\\s*(INV-\\d+)\\s*\\|'
    """)
    ds = scan(load(root / "driftguard.toml"))
    assert ds.all_ids("REQ") == ["REQ-001"]
    assert ds.all_ids("ADR") == ["ADR-0001"]
    assert ds.all_ids("BP") == ["BP-001"]
    assert ds.all_ids("INV") == ["INV-1"]
    assert ds.titles["ADR-0001"] == "One tool, not two"
    assert ds.titles["INV-1"] == "one tool"
    assert ds.titles["BP-001"] == "Skeleton"
    assert ds.titles["REQ-001"] == "The system shall load. See ADR-0001 and BP-001"
    assert ds.referenced_from("ADR-0001") == ["docs/SPEC.md"]
    assert ds.findings == []


def test_def_prefix_for_table_rows_and_filename_check(project) -> None:
    root = project({
        "docs/DECISIONS.md": "| ADR | Decision | Status |\n| --- | --- | --- |\n| 0001 | first | active |\n",
        "docs/decisions/wrong-name.md": "# ADR-0002 — misfiled\n",
    }, toml="""
        docs = ["docs/**/*.md"]
        [[id_classes]]
        name = "ADR"
        ref = '\\bADR-\\d{4}\\b'
        def = '(?m)^\\|\\s*(\\d{4})\\s*\\|'
        def_prefix = "ADR-"
        def_files = ["docs/DECISIONS.md"]
        [[id_classes]]
        name = "ADRF"
        ref = '\\bADR-\\d{4}\\b'
        def = '(?m)^# (ADR-\\d{4})\\b'
        def_files = ["docs/decisions/*.md"]
        filename_must_match = true
    """)
    ds = scan(load(root / "driftguard.toml"))
    assert ds.all_ids("ADR") == ["ADR-0001"]
    assert [f.check for f in ds.findings] == ["DG-FILENAME"]


def test_tombstones_from_table_marker_prose_and_frontmatter(project) -> None:
    root = project({
        "docs/DECISIONS.md": """
            | ADR | Decision | Status |
            | --- | --- | --- |
            | ADR-0001 | Go | superseded-by ADR-0002 |
            | ADR-0002 | Python | active |
            Note: ADR-0003 supersedes ADR-0004 entirely.
            """,
        "docs/decisions/ADR-0005-old.md": "---\nstatus: superseded-by ADR-0002\n---\n# ADR-0005 — old\n",
    })
    ds = scan(load(root / "driftguard.toml"))
    assert ds.tombstones == {"ADR-0001", "ADR-0004", "ADR-0005"}


def test_legacy_tokens_reported(project) -> None:
    root = project({"docs/SPEC.md": "See §3 for details.\n"})
    ds = scan(load(root / "driftguard.toml"))
    assert [f.check for f in ds.findings] == ["DG-LEGACY"]


def test_sections_split_at_same_or_higher_level() -> None:
    secs = sections("# T\n\n## A\nbody a\n### A1\nsub\n## B\nbody b\n")
    names = [(s.title, s.level) for s in secs]
    assert names == [("T", 1), ("A", 2), ("A1", 3), ("B", 2)]
    assert "sub" in secs[1].body and "body b" not in secs[1].body
