from __future__ import annotations

REGISTER_TOML = """
[[registries]]
name = "ids"
kind = "id_register"
output = "docs/generated/ID_REGISTER.md"
backlinks = true
"""


def test_register_renders_and_does_not_create_duplicate_defs(project, run) -> None:
    root = project({
        "docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist per ADR-0001.\n",
        "docs/decisions/ADR-0001-x.md": "# ADR-0001 — X\n",
    }, extra_toml=REGISTER_TOML)
    code, out, _err = run("check")
    assert code == 1 and "DG-REGISTRY-MISSING" in out
    code, out, _err = run("write", "ids")
    assert code == 0, out
    md = (root / "docs/generated/ID_REGISTER.md").read_text()
    assert "## REQ (1)" in md and "| `REQ-001` | The system shall exist per ADR-0001 | docs/SPEC.md |" in md
    assert "| `ADR-0001` | docs/SPEC.md |" in md  # backlink
    code, out, _err = run("check")
    assert code == 0, out  # the register's own rows are refs, never defs
