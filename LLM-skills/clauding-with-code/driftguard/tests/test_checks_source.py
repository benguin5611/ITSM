from __future__ import annotations

LEAKS_TOML = """
[leaks]
globs = ["src/**/*.py"]
"""
ADOPTION_TOML = """
[[adoption]]
name = "subprocess"
pattern = 'subprocess\\.run\\('
glob = ["src/**/*.py"]
allow_files = ["src/procutil.py"]
justification_pattern = '(?i)deliberately not .*run_checked'
message = "route subprocess calls through procutil.run_checked()"
"""


def test_leak_in_comment_or_string_flagged_code_and_markdown_not(project, run) -> None:
    project({
        "docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n",
        "src/a.py": "x = 1  # implements REQ-001\nevidence = 'per ADR-0002'\nreq_001 = 2\n",
        "src/notes.md": "REQ-001 is fine here\n",
    }, extra_toml=LEAKS_TOML)
    code, out, _err = run("check")
    assert code == 1
    assert "src/a.py:1: DG-LEAK" in out and "src/a.py:2: DG-LEAK" in out
    assert "src/a.py:3" not in out and "notes.md" not in out


def test_adoption_census_unjustified_fails_justified_in_function_passes_allow_file_exempt(project, run) -> None:
    project({
        "docs/SPEC.md": "",
        "src/bad.py": "def go():\n    return subprocess.run(['ls'])\n",
        "src/fine.py": "def go():\n    # deliberately not using run_checked: exit code is ambiguous\n    return subprocess.run(['ls'])\n",
        "src/other.py": "def other():\n    # deliberately not using run_checked\n    return 1\n\ndef go():\n    return subprocess.run(['ls'])\n",
        "src/procutil.py": "def run_checked():\n    return subprocess.run(['ls'])\n",
    }, extra_toml=ADOPTION_TOML)
    code, out, _err = run("check")
    assert code == 1
    hits = [ln for ln in out.splitlines() if "DG-ADOPTION" in ln]
    assert len(hits) == 2
    assert any("src/bad.py:2" in h for h in hits) and any("src/other.py:6" in h for h in hits)
