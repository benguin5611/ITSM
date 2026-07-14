# ITSM

Tools to help a Department of One manage a fleet.

## About

Scripts, configs, and small utilities for running IT service management when "IT" is one person and a fleet of laptops, identity providers, MDM consoles, and SaaS admin panels. Built for my own use, shared publicly in case any of it is useful to others in the same position.

A few principles:

- Short scripts you can read in one sitting, not frameworks.
- Lean on vendor APIs and existing tools rather than reinvent them.
- Keep a human in the loop where automation can plausibly get things wrong.

## Contents

### [docs-kit/](docs-kit/)

Documentation for a solo IT operator's core workflows: the paper stack for onboarding, access management, vendor due diligence, and incident response. Organised by a layer model (Policy → Standard → Process/Procedure → Register → Reference); see the [docs-kit README](docs-kit/README.md) for the full index. Companion to [security-grc-kit](https://github.com/benguin5611/security-grc-kit), which carries the security/GRC-audience half of the same documentation system.

**This is a Department-of-One starting point, not a certified or audit-ready compliance program**; see [docs-kit's disclaimer](docs-kit/README.md#before-you-rely-on-anything-here) before relying on anything in it.

### [devices/](devices/)

Docs and tooling for the device fleet: workstations, MDM, and anything that runs on a developer's machine. Storage cleanup guides, network diagnostics, SBOM collection, MDM audit and remediation scripts.

### [LLM-skills/](LLM-skills/)

Reusable Claude skills, drop-in compatible with any Anthropic-skills-aware runtime (Claude Code, the Agent SDK, Cursor, Amp, and others). Current skills:

- **[rainbow-team-review](LLM-skills/rainbow-team-review/)** — ten-agent adversarial review for any plan, decision, or approach
- **[owasp-top-10](LLM-skills/owasp-top-10/)** — security analysis against OWASP Web 2025, API 2023, and LLM AI 2025
- **[knowledge-matrix](LLM-skills/knowledge-matrix/)** — engineering knowledge heatmap from GitHub PR history
- **[help-centre-article](LLM-skills/help-centre-article/)** — write and audit Zendesk Guide articles using the Diátaxis framework
- **[write-like-a-human](LLM-skills/write-like-a-human/)** — detect and remove AI-writing tells
- **[business-case](LLM-skills/business-case/)** — structured business case and vendor decision workflow
- **[custom-json-schema](LLM-skills/custom-json-schema/)** — build and audit JSON schemas with pluggable domain documentation
- **[jobs-to-be-done](LLM-skills/jobs-to-be-done/)** — compact Jobs-to-be-Done analyses in the Klement/Christensen Job Story school, with good/better/best tiering
- **[clauding-with-code](LLM-skills/clauding-with-code/)** — phased build orchestrator for shipping a feature end to end with an AI coding agent, project-agnostic
- **[meta-code-review](LLM-skills/meta-code-review/)** — orchestrates multiple review lenses against the real code into one human-in-the-loop verdict, with a deterministic dead-code emitter census
- **[playwright-demo-recorder](LLM-skills/playwright-demo-recorder/)** — record narrated product-demo videos: Playwright drives the UI, macOS `say` generates inline voiceover paced to narration length, ffmpeg muxes one deliverable

## Licence

Mixed, scoped to content type: the code (`devices/`, `LLM-skills/`) is **MIT** (see [LICENSE](LICENSE)). The `docs-kit/` subtree is **CC BY 4.0**, the correct licence family for a prose-and-templates kit (see [docs-kit/README.md](docs-kit/README.md#licensing)).
