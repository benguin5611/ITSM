from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import BASE_TOML
from driftguard import __version__


def test_json_output_shape_and_only_filter(project, run) -> None:
    project({"docs/SPEC.md": "**REQ-001 (Ubiquitous).** Users log in. See REQ-002 and §4.\n"})
    code, out, _err = run("check", "--json")
    assert code == 1
    data = json.loads(out)
    assert data["ok"] is False and data["defs"] == {"REQ": 1, "ADR": 0, "BP": 0}
    assert {f["check"] for f in data["findings"]} == {"DG-EARS", "DG-DANGLING", "DG-LEGACY"}
    code, out, _err = run("check", "--only", "DG-LEGACY")
    assert code == 1 and out.count("DG-") == 1


def test_write_unknown_registry_is_usage_error(project, run) -> None:
    project({"docs/SPEC.md": "x\n"})
    code, _out, err = run("write", "nope")
    assert code == 2 and "no registry named 'nope'" in err


def test_console_entry_point_version(tmp_path: Path) -> None:
    r = subprocess.run([sys.executable, "-m", "driftguard.cli", "--version"], capture_output=True, text=True, check=False)
    assert r.returncode == 0 and __version__ in r.stdout


def test_plugin_checks_run_and_bad_plugins_are_usage_errors(project, run, tmp_path: Path) -> None:
    root = project({"docs/SPEC.md": "x\n", "tools/__init__.py": "", "tools/extra.py": """
        from driftguard import Finding
        def shout(ctx):
            return [Finding("docs/SPEC.md", 1, "PLUG-1", "custom")]
        CHECKS = [shout]
        """}, toml='plugins = ["tools.extra"]\n' + BASE_TOML)  # a top-level key must precede the tables
    code, out, _err = run("check")
    assert code == 1 and "docs/SPEC.md:1: PLUG-1: custom" in out
    (root / "tools/extra.py").write_text("NOPE = 1\n")
    for m in ("tools", "tools.extra"):  # in-process runs share the import cache; a real CLI run does not
        sys.modules.pop(m, None)
    code, _out, err = run("check")
    assert code == 2 and "has no CHECKS list" in err
    (root / "driftguard.toml").write_text((root / "driftguard.toml").read_text().replace("tools.extra", "tools.missing"))
    code, _out, err = run("check")
    assert code == 2 and "failed to import" in err
