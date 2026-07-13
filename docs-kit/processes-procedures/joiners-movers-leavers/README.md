---
Artefact type: Procedure (index)
Owner role: IT operator
Review cadence: Annual, or on material tooling change
Version: 1.0 (template)
---

# Joiners / Movers / Leavers

> Part of the [docs-kit](../../README.md#before-you-rely-on-anything-here) — a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer, and each procedure's own "Adapt this to your context" section, before relying on it.

The three highest-frequency, highest-risk identity workflows a solo IT operator runs. Each is a standalone checklist:

- [Joiners (onboarding)](joiners.md)
- [Movers (role change)](movers.md)
- [Leavers (offboarding)](leavers.md)

All three assume a per-user record in the [Company Asset Register](../../registers/company-asset-register.md) — the register is where access, device assignment, and ownership actually get tracked; these procedures just say when to touch it and how.

None of these procedures name a specific identity provider, MDM, or ticketing tool. Every step that needs one describes what the tool must do (suspend an account, enforce a group membership, log a request) rather than how to click through a specific vendor's console — the mechanics change with your stack; the discipline underneath them doesn't.
