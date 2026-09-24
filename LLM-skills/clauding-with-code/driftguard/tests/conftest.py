from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

import pytest

import driftguard.scan as scanmod
from driftguard import cli

BASE_TOML = """
docs = ["docs/**/*.md"]

[[id_classes]]
name = "REQ"
ref = '\\bREQ-\\d{3}\\b'
def = '(?m)^\\*\\*(REQ-\\d{3})\\b'
ears = true
allocate = true

[[id_classes]]
name = "ADR"
ref = '\\bADR-\\d{4}\\b'
def = '(?m)^# (ADR-\\d{4})\\b'
def_files = ["docs/decisions/*.md"]
filename_must_match = true
allocate = true

[[id_classes]]
name = "BP"
ref = '\\bBP-\\d{3}\\b'
def = '(?m)^\\*\\*(BP-\\d{3}) \\(Phase'
"""


@pytest.fixture
def project(tmp_path: Path):
    """Write a doc tree plus driftguard.toml under tmp_path; returns tmp_path."""

    def make(files: dict[str, str], toml: str = BASE_TOML, extra_toml: str = "") -> Path:
        for rel, content in files.items():
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
        (tmp_path / "driftguard.toml").write_text(textwrap.dedent(toml) + "\n" + textwrap.dedent(extra_toml), encoding="utf-8")
        return tmp_path

    return make


@pytest.fixture
def run(tmp_path: Path, capsys):
    """Run the CLI in-process against tmp_path/driftguard.toml. Returns (exit, stdout, stderr)."""

    def _run(*argv: str, config: str | None = None) -> tuple[int, str, str]:
        cfg = config or str(tmp_path / "driftguard.toml")
        args = list(argv)
        if args and args[0] == "write":
            args = ["write", args[1], "--config", cfg, *args[2:]]
        else:
            args = [*args, "--config", cfg]
        code = cli.main(args)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


class FakeProc:
    """Stand-in for scan.run_cmd: canned CompletedProcess per argv predicate; unknown → 127."""

    def __init__(self) -> None:
        self.rules: list = []
        self.calls: list[list[str]] = []

    def on(self, predicate, stdout: str = "", returncode: int = 0, stderr: str = "") -> None:
        self.rules.append((predicate, stdout, returncode, stderr))

    def gh_titles(self, state: str, titles: list[str]) -> None:
        self.on(lambda a: a[:2] == ["gh", "pr"] and state in a, json.dumps([{"title": t} for t in titles]))

    def __call__(self, argv, cwd, timeout=60):
        self.calls.append(list(argv))
        for pred, so, rc, se in self.rules:
            if pred(argv):
                return subprocess.CompletedProcess(argv, rc, so, se)
        return subprocess.CompletedProcess(argv, 127, "", f"{argv[0]}: not found")


@pytest.fixture
def fake_proc(monkeypatch: pytest.MonkeyPatch) -> FakeProc:
    fake = FakeProc()
    monkeypatch.setattr(scanmod, "run_cmd", fake)
    return fake


GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_OBJECT_DIRECTORY",
           "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR")


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A real git repo at tmp_path with an initial commit; returns a commit(message) helper.

    When pytest itself runs inside a git hook, git's own environment would point every nested git
    call at the outer repo, so it is stripped for the whole test."""
    for var in GIT_ENV:
        monkeypatch.delenv(var, raising=False)

    def git(*args: str) -> str:
        r = subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, check=False)
        assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
        return r.stdout

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    git("config", "commit.gpgsign", "false")

    def commit(message: str = "c") -> str:
        git("add", "-A")
        git("commit", "-q", "--allow-empty", "-m", message)
        return git("rev-parse", "HEAD").strip()

    commit.git = git  # type: ignore[attr-defined]
    return commit
