---
Artefact type: Register
Owner role: IT operator
Review cadence: Continuous (updated whenever a document is created, changed, or retired); each document's own cadence drives its next review, checked at least annually
Version: 1.0 (template)
---

# Policy and documentation register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

One list of every governing document you maintain: what it is, who owns it, what version is current, and when it's next due for review, so nothing quietly goes stale or gets applied from an outdated copy.

## Columns

| Column | Purpose |
| --- | --- |
| Document ID | A short reference so the document can be cited (in an audit, a policy cross-reference, or a ticket) without repeating its full title. |
| Document name | The title of the policy, standard, process, procedure, register, or reference material. |
| Type | Which layer of the documentation model it sits in (Policy, Standard, Process, Procedure, Register, or Reference), so the register doubles as an index of the whole library. |
| Owner | The person accountable for the document's content staying accurate and current. |
| Approver | Whoever signed off the version currently in force (often more senior than the owner). |
| Version | The version number currently in effect. |
| Status | Draft, In review, Approved, Superseded, or Retired. |
| Effective date | When the current version came into force. |
| Review cadence | How often this specific document is due for review, e.g. annually, or on major change. |
| Next review due | The date the next review is due, calculated from the cadence. |
| Location | A link to where the current version actually lives. Never a copy pasted into the register itself. |

## Worked example

| Document ID | Document name | Type | Owner | Approver | Version | Status | Effective date | Review cadence | Next review due | Location |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| POL-014 | Information & Cyber Security Policy | Policy | J. Alderton | M. Delacroix (Managing Director) | 2.1 | Approved | 2026-02-01 | Annual | 2027-02-01 | `docs-kit/policies/...` |
| STD-021 | Identity and Access Management Standard | Standard | J. Alderton | J. Alderton | 1.3 | Approved | 2025-09-15 | Annual | 2026-09-15 | `docs-kit/standards/...` |
| PROC-033 | Joiners / Movers / Leavers Procedure | Procedure | S. Nakamura | J. Alderton | 3.0 | Draft | N/A | Annual | N/A | `docs-kit/procedures/...` |
| REG-041 | Company Asset Register | Register | S. Nakamura | S. Nakamura | 1.4 | Approved | 2026-01-10 | Semi-annual | 2026-07-10 | `docs-kit/registers/...` |

## Adapt this to your context

- **Size and maturity**: a handful of rows is fine as a flat list; once the library grows past what one person tracks from memory, filter by "Type" rather than standing up a second register.
- **Compliance program**: if you're pursuing a specific certification, that framework's document-control requirements (approval, version history, retention of superseded copies) may be stricter than what's listed here. Confirm current requirements before relying on this as your whole document-control process.
- **Jurisdiction and industry**: record-retention rules for superseded policies vary. Check what you're legally required to keep, and for how long, before deleting a "Retired" row rather than just marking it.
- **Regulated or audited environments**: an auditor usually wants to see that the version in force matches what was actually approved. Keep the Location link pointing at the single source of truth to prevent drift from a stray copy.

**Frameworks referenced**: ISO/IEC 27001 and ISO 9001's documented-information and document-control requirements; SOC 2's policy-management criteria
