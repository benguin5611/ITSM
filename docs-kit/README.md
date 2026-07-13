# docs-kit

Documentation for a solo IT operator's core workflows — the paper stack that lets one person run onboarding, access, vendor checks, and incident response defensibly, without a GRC platform or a team behind them.

## Before you rely on anything here

**This kit is designed to get a Department of One from nothing to something defensible — fast. It is a starting point, not a finished compliance program, and it is not designed to be bulletproof.**

- Every artefact here is deliberately simplified to be usable by one person with no budget and no compliance team behind them. That means some choices are pragmatic defaults chosen for that context, not necessarily the most rigorous option a larger, better-resourced function would pick.
- Some content may diverge — intentionally or otherwise — from what a specific standard, framework, contract, or auditor expects. Every artefact ends with an **"Adapt this to your context"** section; that's not optional reading, it's where the load-bearing caveats live.
- Don't put anything here in front of an auditor, regulator, customer, or board as a certified or audit-ready control without reviewing and adapting it yourself first.
- Where a specific compliance program, contract, or regulator requires something stricter than what's written here, that requirement wins. This kit is a floor to build from, not a ceiling.

## Why this exists

A department of one still has to answer the same questions an enterprise IT function does: who has access to what, why, and who approved it. This kit is a from-scratch, generic answer to that — written to be forked and adapted by any solo operator, not built around any one organisation's setup.

Every artefact here is written to stand on its own. If something would only make sense stripped down to a hollow shell, it isn't shipped at all — quality over count.

## The documentation model

This kit — and its companion, [security-grc-kit](https://github.com/benguin5611/security-grc-kit) — are organised by altitude and sponsorship, not by topic:

| Layer | Altitude | Owned by | Answers |
|---|---|---|---|
| **Policies** | Strategic, deliberately generic | Executive-sponsored | Why does this function exist, and what does it commit to? |
| **Standards** | Tactical | IT/Security lead | Per-control directives, split into **Requirements** (must/shall) and **Guidelines** (should/may/can). |
| **Processes & Procedures** | Implementation, changes often | The operator | A *Process* is input → sub-process → output. A *Procedure* is the checklist for how a task in that process is actually done. |
| **Registers** | Operational record | The operator | The listings that track value, location, ownership, and access. |
| **References** | Supporting material | — | Templates and material that fit no other layer. |

ISO 27001 / an ISMS is one prominent use case for this taxonomy, not a prerequisite — it's a general-purpose way to structure any small function's documentation.

## What's here (Tier 1 — the irreducible core)

| Artefact | Layer |
|---|---|
| [Information & Cyber Security Policy](policies/information-and-cyber-security-policy.md) | Policy |
| [Identity and Access Management Standard](standards/identity-and-access-management-standard.md) | Standard |
| [Joiners / Movers / Leavers](processes-procedures/joiners-movers-leavers/) | Procedure |
| [Endpoint Privileged Access Management](processes-procedures/endpoint-privileged-access-management.md) | Procedure |
| [Access Management & Review](processes-procedures/access-management-and-review.md) | Procedure |
| [Software Onboarding & Vendor Due Diligence](processes-procedures/software-onboarding-and-vendor-due-diligence.md) | Procedure |
| [Password Reset & Identity Verification](processes-procedures/password-reset-and-identity-verification.md) | Procedure |
| [Incident Response Plan](processes-procedures/incident-response-plan.md) | Plan |
| [Company Asset Register](registers/company-asset-register.md) | Register |
| [Post-Incident Report Template](references/post-incident-report-template.md) | Reference |

Tier 2 (the operator's standards library) and Tier 3 (the evidence-spine registers and references) are future passes.

## Relationship to security-grc-kit

This kit and [security-grc-kit](https://github.com/benguin5611/security-grc-kit) are two audience-scoped halves of one documentation system, split by **audience, not topic**:

- **This kit** → a solo IT operator / department of one. Ships the operational checklist/template.
- **security-grc-kit** → a security/GRC practitioner. Ships the method/model/analysis behind it.

Where a topic touches both (vendor due diligence, risk, incident response, access review), this kit carries the operational checklist and register, and security-grc-kit carries the deeper method — each side notes the other rather than forking the same content twice. For example, this kit's software onboarding procedure carries the operational vendor check; security-grc-kit's (forthcoming) third-party risk model carries the quantitative CIA × jurisdiction × adverse-history scoring behind it.

## Licensing

This subtree is **CC BY 4.0** (see the note in the repo root [LICENSE](../LICENSE) area) — the rest of this repository (the SBOM pipeline and LLM skills) stays **MIT**. Applying a software licence to a prose and template kit is a category error; CC BY 4.0 is the Creative Commons tier built for maximum reuse.
