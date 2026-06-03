# ITSM

Tools to help a Department of One manage a fleet.

## About

Scripts, configs, and small utilities for running IT service management when "IT" is one person and a fleet of laptops, identity providers, MDM consoles, and SaaS admin panels. Built for my own use, shared publicly in case any of it is useful to others in the same position.

A few principles:

- Short scripts you can read in one sitting, not frameworks.
- Lean on vendor APIs and existing tools rather than reinvent them.
- Keep a human in the loop where automation can plausibly get things wrong.

## Contents

### [devices/](devices/)

Docs and tooling for the device fleet — workstations, MDM, and anything that runs on a developer's machine. Storage cleanup guides, network diagnostics, SBOM collection, MDM audit and remediation scripts.

### [LLM-skills/](LLM-skills/)

Reusable Claude skills — drop-in compatible with any Anthropic-skills-aware runtime (Claude Code, the Agent SDK, Cursor, Amp, and others). Current skills:

- **[rainbow-team-review](LLM-skills/rainbow-team-review/)** — ten-agent adversarial review for any plan, decision, or approach
- **[owasp-top-10](LLM-skills/owasp-top-10/)** — security analysis against OWASP Web 2025, API 2023, and LLM AI 2025
- **[knowledge-matrix](LLM-skills/knowledge-matrix/)** — engineering knowledge heatmap from GitHub PR history
- **[help-centre-article](LLM-skills/help-centre-article/)** — write and audit Zendesk Guide articles using the Diátaxis framework
- **[write-like-a-human](LLM-skills/write-like-a-human/)** — detect and remove AI-writing tells
- **[business-case](LLM-skills/business-case/)** — structured business case and vendor decision workflow
- **[custom-json-schema](LLM-skills/custom-json-schema/)** — build and audit JSON schemas with pluggable domain documentation

## Licence

MIT — see [LICENSE](LICENSE).
