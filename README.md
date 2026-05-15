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

Docs and tooling for the device fleet — workstations, MDM, and anything that runs on a developer's machine.

- **[devices/macos-storage-cleanup.md](devices/macos-storage-cleanup.md)** — practical guide to diagnosing high disk usage on macOS and reclaiming space safely. APFS volume structure, snapshots, language toolchain caches, IDE caches, and what's safe to delete.
- **[devices/sbom/](devices/sbom/)** — automated monthly SBOM collection from macOS developer machines in SPDX 2.3 format. Scans the Nix profile via [sbomnix](https://github.com/tiiuae/sbomnix) and every package manager [Syft](https://github.com/anchore/syft) supports (Homebrew, pip, npm, Go modules, Cargo, Ruby gems, Java, Cocoapods, and more). On-device bash script, Go Lambda that issues presigned URLs and validates uploads, and Terraform for the S3 bucket, IAM, KMS, logs, alarms, and secrets.

### [LLM-skills/](LLM-skills/)

Reusable Claude skills for engineering, security, and decision-making work — adversarial plan review, OWASP security analysis, AI-writing cleanup, business cases, and JSON schema authoring. Domain-agnostic, drop-in compatible with any Anthropic-skills-aware runtime.

Each subfolder has its own README covering deployment, operations, and any gotchas.

## Licence

MIT — see [LICENSE](LICENSE).
