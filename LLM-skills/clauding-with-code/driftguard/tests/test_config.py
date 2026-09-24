from __future__ import annotations

from pathlib import Path

import pytest

from driftguard.config import ConfigError, _fnmatch, load


def test_missing_config_is_a_usage_error(run, tmp_path: Path) -> None:
    code, _out, err = run("check", config=str(tmp_path / "nope.toml"))
    assert code == 2 and "config not found" in err


def test_unknown_top_level_key(project, run) -> None:
    project({}, toml='docs = ["docs/*.md"]\nbogus = 1\n')
    code, _out, err = run("check")
    assert code == 2 and "unknown top-level keys" in err


def test_bad_regex(project, run) -> None:
    project({}, toml='docs = ["docs/*.md"]\n[[id_classes]]\nname = "X"\nref = "("\ndef = "x"\n')
    code, _out, err = run("check")
    assert code == 2 and "bad regex" in err


def test_docs_required(project) -> None:
    root = project({}, toml="exclude = []\n")
    with pytest.raises(ConfigError, match="'docs'"):
        load(root / "driftguard.toml")


def test_registry_kind_validated(project, run) -> None:
    project({}, toml='docs = ["docs/*.md"]\n[[registries]]\nkind = "nope"\noutput = "x.md"\n')
    code, _out, err = run("check")
    assert code == 2 and "kind must be one of" in err


def test_paths_resolve_relative_to_the_config_file(project, monkeypatch, tmp_path: Path) -> None:
    root = project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** The system shall exist.\n"})
    monkeypatch.chdir(tmp_path.parent)  # a different cwd must not matter
    cfg = load(root / "driftguard.toml")
    assert cfg.doc_files() == ["docs/SPEC.md"]


def test_fnmatch_handles_double_star() -> None:
    assert _fnmatch("docs/a.md", "docs/**/*.md")
    assert _fnmatch("docs/x/y/a.md", "docs/**/*.md")
    assert not _fnmatch("other/a.md", "docs/**/*.md")
