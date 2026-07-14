---
Artefact type: Procedure (index)
Owner role: IT operator
Review cadence: Annual, or on material tooling change
Version: 1.0 (template)
---

# Joiners / Movers / Leavers

> Part of the [docs-kit](../../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer, and each procedure's own "Adapt this to your context" section, before relying on it.

The three highest-frequency, highest-risk identity workflows a solo IT operator runs. Each procedure is a standalone checklist, paired with its own process diagram showing the cross-functional workflow it sits inside:

- [Joiners (onboarding)](joiners.md) (process: [joiners-process.md](../../processes/joiners-movers-leavers/joiners-process.md))
- [Movers (role change)](movers.md) (process: [movers-process.md](../../processes/joiners-movers-leavers/movers-process.md))
- [Leavers (offboarding)](leavers.md) (process: [leavers-process.md](../../processes/joiners-movers-leavers/leavers-process.md))

All three assume a per-user record in the [Company Asset Register](../../registers/company-asset-register.md). The register is where access, device assignment, and ownership actually get tracked; these procedures just say when to touch it and how.

None of these procedures name a specific identity provider, MDM, or ticketing tool. Every step that needs one describes what the tool must do (suspend an account, enforce a group membership, log a request) rather than how to click through a specific vendor's console. The mechanics change with your stack; the discipline underneath them doesn't.
