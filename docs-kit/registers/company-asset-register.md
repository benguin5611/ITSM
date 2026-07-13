---
Artefact type: Register
Owner role: IT operator
Review cadence: Continuous (updated on every joiner/mover/leaver/onboarding event); formally reviewed annually
Version: 1.0 (template)
---

# Company asset register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here) — a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The single spreadsheet a solo operator most needs and least often has — one place that answers "what do we have, who has access to what, and who's accountable for it" without needing a GRC platform.

## Read this before you build one

A spreadsheet is a starting point, not the destination. As the fleet and system count grow, purpose-built tools do this job far better than a shared sheet ever will:

- **Hardware/device tracking** — a proper MDM (Kandji, Jamf, Intune, etc.) is already your source of truth for enrolment status, OS version, and encryption state; a tool like Snipe-IT adds procurement, warranty, and assignment history on top. Don't hand-maintain what your MDM already knows.
- **Access tracking** — your identity provider (Okta, Entra ID, Google Workspace, etc.) or an HRIS-linked identity system is the real system of record for who has access to what. A spreadsheet should be the fallback for the systems that aren't wired into SSO yet, not a shadow copy of what your IdP already tracks correctly.

This template is deliberately the "if you have nothing else yet" version — the minimum structure worth tracking, in a form any solo operator can start using today with no budget and no integration work. Treat outgrowing it as a good sign, not a failure to maintain it properly.

## Design note: track by identity, not by account

The single most common mistake in a first-pass asset register is modelling it **account-first**: one row per login, per system, with no reliable link back to the actual person behind it. That falls apart exactly when it matters most — offboarding a leaver means hunting across every tab for anything that might be theirs, and a stale or orphaned account is invisible until someone notices it by accident.

Model it **identity-first** instead: one row per real person (or per service/non-human identity) as the anchor, with every system username or account they hold mapped underneath that one identity. A mover or leaver event then touches one row, and every account tied to that identity is visible from it — not scattered across a dozen system-specific lists that each need to be checked separately.

## Recommended tabs

| Tab | Purpose | Key columns |
| --- | --- | --- |
| **Identities** | One row per real person or service identity — the anchor for everything else. | Identity name · Type (staff / contractor / service) · Start date · End date · Line manager · Status (active / suspended / offboarded) |
| **User Access** | Every system username/account, joined back to an Identity. Flag elevated/privileged access clearly — a distinct colour or a dedicated column, not just a note buried in a comment. | Identity (link) · System (link) · Username/account · Access level · Elevated? (Y/N) · Granted date · Approved by · Last reviewed |
| **Systems** | Every system or piece of software in use. | System name · Vendor · Owner · Criticality/CIA rating (see [Software Onboarding & Vendor Due Diligence](../processes-procedures/software-onboarding-and-vendor-due-diligence.md)) · Licence/subscription renewal date · Status (active / decommissioned) |
| **Hardware** | Every device. | Asset tag · Type · Assigned identity (link) · Serial number · Purchase/warranty date · Status (assigned / spare / decommissioned) |
| **Tier 1 suppliers** | Vendors material enough to need active oversight, distinct from every SaaS tool. | Supplier name · Service provided · Contract/renewal date · Last due-diligence review date · Risk notes |

Add a **Status** or **Decommissioned** flag rather than moving rows to a separate archive tab as they age out — it keeps history queryable in one place instead of doubling the number of tabs you maintain.

## What this deliberately leaves out

A real, mature asset register grows well beyond these five tabs — API keys and secrets, cloud infrastructure environments, per-provider federation/environment tracking, and a dedicated RBAC-profile tab are all things a larger estate ends up tracking somewhere. They're excluded here on purpose:

- **API keys and secrets** belong in a secrets manager, not a spreadsheet, for the same reason passwords don't belong in one — a spreadsheet has no rotation enforcement, no access logging, and no encryption at rest. If you need a lightweight register of *what* secrets exist and who owns them (without storing the secret values themselves), that's a reasonable fifth tab; the secret values never are.
- **Cloud infrastructure environments** are usually already tracked by your infrastructure-as-code tooling or cloud provider console — duplicating that into a spreadsheet just creates a second, decaying source of truth.
- **RBAC profiles** can live as a column on the User Access tab (which profile an access grant maps to) rather than a fully separate tab, until the number of profiles genuinely outgrows that.

Track what you need, not what a bigger estate eventually accumulates — a register nobody keeps current is worse than a smaller one that's actually trustworthy.

## Adapt this to your context

- **Regulated industries**: audit-trail and record-retention requirements for a register like this vary by sector and jurisdiction — check what you're required to retain (and for how long) before purging old rows, even from a "decommissioned" status flag.
- **Compliance program**: if you're pursuing a specific certification, that framework may prescribe minimum fields for an asset inventory (e.g. an explicit owner and classification per asset) beyond what's listed here — check the current requirements of whichever framework applies.
- **Size and maturity**: treat "move to purpose-built tooling" as the direction of travel, not an optional nice-to-have, once you're past a handful of systems and devices — a spreadsheet's lack of access logging and enforced structure becomes a real audit gap at a certain scale, not just an inconvenience.

**Frameworks referenced**: ISO/IEC 27001 Annex A's asset-management objectives.
