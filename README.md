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

Reusable Claude skills — drop-in compatible with any Anthropic-skills-aware runtime (Claude Code, the Agent SDK). Currently: writing Zendesk-bound help centre articles using the Diátaxis framework.

## Licence

MIT — see [LICENSE](LICENSE).
