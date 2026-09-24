"""Every template the skill ships must fail `driftguard check` while bare (its placeholders are
empty by definition) and pass once filled — otherwise the template and the checker disagree."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
SKILL = PKG.parent
TEMPLATES = SKILL / "templates"
EXAMPLES = PKG / "examples"
PLACEHOLDER = re.compile(r"<[^<>\n]{1,80}>")


def fill(text: str, overrides: dict[str, str] | None = None) -> str:
    ov = overrides or {}

    def sub(m: re.Match[str]) -> str:
        key = m.group(0)[1:-1].strip()
        for k, v in ov.items():
            if key.startswith(k):
                return v
        return "filled"

    return PLACEHOLDER.sub(sub, text)


def _section_codes(out: str) -> set[str]:
    return {ln.split(": ")[1] for ln in out.splitlines() if ": DG-" in ln}


def _light(tmp_path: Path, filled: bool) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    ov = {"status": "verified", "signed-off": "signed-off: Ben, 2026-09-02", "requirements": "**REQ-001 (Ubiquitous).** The system shall run the gate."}
    for src, dst in (("SPEC-light.md", "SPEC.md"), ("binding.md", "binding.md")):
        text = (TEMPLATES / src).read_text()
        (docs / dst).write_text(fill(text, ov) if filled else text)
    shutil.copy(EXAMPLES / "light.toml", tmp_path / "driftguard.toml")


def test_light_templates_bare_fail_and_filled_pass(tmp_path: Path, run, fake_proc) -> None:
    fake_proc.gh_titles("merged", [])
    fake_proc.gh_titles("open", [])
    _light(tmp_path, filled=False)
    code, out, _err = run("check")
    assert code == 1
    for doc in ("docs/SPEC.md", "docs/binding.md"):
        assert any(ln.startswith(doc) and "DG-SECTION" in ln for ln in out.splitlines()), (doc, out)
    _light(tmp_path, filled=True)
    code, out, _err = run("check")
    assert code == 0, out


def _doc_set(tmp_path: Path, filled: bool) -> None:
    docs = tmp_path / "docs"
    (docs / "decisions").mkdir(parents=True, exist_ok=True)
    ov = {"status": "verified", "signed-off": "signed-off: Ben, 2026-09-02",
          "requirements": "### OPS\n\n**REQ-OPS-001 (Ubiquitous).** The system shall run the gate.",
          "INV-N": "INV-1", "ADR-NNNN": "ADR-0001", "REQ": "REQ-OPS-001"}
    for src in ("SPEC.md", "CONVENTIONS.md", "DEPENDENCIES.md"):
        text = (TEMPLATES / "doc-set" / src).read_text()
        (docs / src).write_text(fill(text, ov) if filled else text)
    for src in ("binding.md",):
        text = (TEMPLATES / src).read_text()
        (docs / src).write_text(fill(text, ov) if filled else text)
    adr = (TEMPLATES / "doc-set" / "decisions" / "ADR-0000-template.md").read_text().replace("ADR-0000", "ADR-0001")
    (docs / "decisions" / "ADR-0001-gate.md").write_text(fill(adr) if filled else adr)
    plan = json.loads((TEMPLATES / "doc-set" / "build_plan.json").read_text())
    if filled:
        plan["build_rules"][0]["text"] = "run the gate"
        ph = plan["phases"][0]
        ph["title"] = "Skeleton"
        ph["tier2"] = {k: "ADR-0001" for k in ph["tier2"]}
        ph["steps"][0].update(title="Wire the gate", body_md="- **Do:** wire it", discharges=["REQ-OPS-001"])
    (docs / "build_plan.json").write_text(json.dumps(plan))
    (docs / "bug_registry.json").write_text(json.dumps({"rows": []}))
    shutil.copy(TEMPLATES / "doc-set" / "driftguard.toml", tmp_path / "driftguard.toml")


def test_doc_set_templates_bare_fail_and_filled_pass_including_registries(tmp_path: Path, run, fake_proc) -> None:
    fake_proc.gh_titles("merged", [])
    fake_proc.gh_titles("open", [])
    _doc_set(tmp_path, filled=False)
    code, out, _err = run("check")
    assert code == 1
    codes = _section_codes(out)
    assert "DG-SECTION" in codes and "DG-REGISTRY-MISSING" in codes
    _doc_set(tmp_path, filled=True)
    for name in ("build_plan", "id_register", "bugs"):
        code, out, _err = run("write", name)
        assert code == 0, (name, out)
    code, out, _err = run("check")
    assert code == 0, out
    index = (tmp_path / "docs/generated/BUILD_PLAN.md").read_text()
    assert "| BP-001 | open | Wire the gate |" in index
    assert (tmp_path / "docs/generated/BUILD_PLAN/phase-00.md").exists()


def test_doc_set_config_template_matches_the_package_example() -> None:
    assert (TEMPLATES / "doc-set" / "driftguard.toml").read_bytes() == (EXAMPLES / "doc-set.toml").read_bytes()


@pytest.mark.parametrize("rel,cap", [
    ("binding.md", 2200), ("discovery-gate.md", 2800), ("SPEC-light.md", 2000), ("session-handover.md", 2000),
    ("doc-set/CONVENTIONS.md", 3000), ("doc-set/SPEC.md", 2500), ("doc-set/AGENTS.md", 1200),
    ("doc-set/DEPENDENCIES.md", 1000), ("doc-set/decisions/ADR-0000-template.md", 800),
    ("doc-set/build_plan.json", 1200), ("doc-set/driftguard.toml", 4000),
])
def test_template_byte_caps(rel: str, cap: int) -> None:
    size = (TEMPLATES / rel).stat().st_size
    assert size <= cap, f"{rel} is {size} bytes, cap {cap}"
