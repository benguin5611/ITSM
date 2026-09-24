from __future__ import annotations

from pathlib import Path

CURRENCY_TOML = """
[currency]
docs = ["docs/DECISIONS.md"]
"""


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def test_currency_fires_only_when_cited_file_changed_and_claim_line_untouched(project, run, git_repo) -> None:
    root = project({
        "docs/DECISIONS.md": "Row: `STRATEGY.md` still says the old mission, not yet re-pointed.\nOther: `CONVENTIONS.md` still lists it.\n",
        "docs/STRATEGY.md": "mission v1\n",
        "docs/CONVENTIONS.md": "c\n",
    }, extra_toml=CURRENCY_TOML)
    git_repo("base")
    _write(root, "docs/STRATEGY.md", "mission v2\n")
    git_repo.git("add", "-A")
    code, out, _err = run("check", "--staged")
    assert code == 1
    assert "docs/DECISIONS.md:1: DG-CURRENCY" in out and "DECISIONS.md:2" not in out

    # touching the claim line in the same diff clears it
    _write(root, "docs/DECISIONS.md", "Row: `STRATEGY.md` still says the old mission, not yet re-pointed — confirmed 2026-09-02.\nOther: `CONVENTIONS.md` still lists it.\n")
    git_repo.git("add", "-A")
    code, out, _err = run("check", "--staged")
    assert code == 0, out


def test_diff_base_and_scope_to_diff(project, run, git_repo) -> None:
    root = project({
        "docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n",
        "docs/OTHER.md": "See REQ-404.\n",
    })
    git_repo("base")
    git_repo.git("branch", "base")
    _write(root, "docs/SPEC.md", "**REQ-001 (Ubiquitous).** The system shall exist.\nAlso REQ-999.\n")
    git_repo("change")
    code, out, _err = run("check", "--diff-base", "base")
    assert code == 1 and "REQ-404" in out and "REQ-999" in out
    code, out, _err = run("check", "--diff-base", "base", "--scope-to-diff")
    assert code == 1 and "REQ-999" in out and "REQ-404" not in out


def test_bad_diff_base_is_a_usage_error(project, run, git_repo) -> None:
    project({"docs/SPEC.md": "x\n"})
    git_repo("base")
    code, _out, err = run("check", "--diff-base", "no-such-ref")
    assert code == 2, (code, err)
    assert "not a commit" in err


def test_scope_to_diff_without_diff_mode_is_a_usage_error(project, run) -> None:
    project({"docs/SPEC.md": "x\n"})
    code, _out, err = run("check", "--scope-to-diff")
    assert code == 2 and "--scope-to-diff" in err


def test_hwm_whole_corpus_merged_and_open_titles(project, run, fake_proc) -> None:
    project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n**REQ-002 (Ubiquitous).** The system shall persist.\n"})
    fake_proc.gh_titles("merged", ["feat: REQ-004 something", "chore: unrelated"])
    fake_proc.gh_titles("open", ["feat: REQ-007 in flight"])
    code, out, _err = run("check")
    assert code == 1
    assert "DG-HWM: a merged PR title spent REQ-4 but the doc set's max is REQ-2" in out
    assert "an open PR title already claims REQ-7" in out


def test_hwm_clean_when_docs_lead(project, run, fake_proc) -> None:
    project({"docs/SPEC.md": "**REQ-009 (Ubiquitous).** The system shall exist.\n"})
    fake_proc.gh_titles("merged", ["REQ-004"])
    fake_proc.gh_titles("open", ["REQ-009 backfill"])
    code, out, _err = run("check")
    assert code == 0, out


def test_hwm_gh_unreachable_is_skipped_not_passed_or_failed(project, run, fake_proc) -> None:
    project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n"})
    code, out, err = run("check", "--json")
    assert code == 0
    assert '"skipped": ["DG-HWM: gh exited 127' in out


def test_hwm_diff_mode_flags_reuse_below_floor_and_allows_backfill(project, run, fake_proc, git_repo) -> None:
    root = project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n"})
    git_repo("base")
    git_repo.git("branch", "base")
    fake_proc.gh_titles("merged", ["REQ-003 shipped earlier"])
    # gh is faked; git must stay real for the diff and the base-ref scan
    import subprocess as sp

    import driftguard.scan as scanmod

    def passthrough(argv, cwd, timeout=60):
        if argv[0] == "git":
            return sp.run(argv, cwd=str(cwd), capture_output=True, text=True, check=False)
        return fake_proc(argv, cwd, timeout)

    scanmod.run_cmd = passthrough  # restored by the fake_proc monkeypatch at teardown
    _write(root, "docs/SPEC.md", "**REQ-001 (Ubiquitous).** The system shall exist.\n**REQ-002 (Ubiquitous).** The system shall reuse.\n**REQ-003 (Ubiquitous).** The system shall backfill.\n**REQ-005 (Ubiquitous).** The system shall advance.\n")
    git_repo("change")
    code, out, _err = run("check", "--diff-base", "base")
    assert code == 1
    assert "docs/SPEC.md:2: DG-HWM: REQ-002 is new in this diff but at or below the high-water mark REQ-3" in out
    assert "REQ-003" not in out.replace("REQ-003 shipped", "") and "REQ-005" not in out
