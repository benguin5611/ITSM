# docs-kit

Documentation for a solo IT operator's core workflows: the paper stack that lets one person run onboarding, access, vendor checks, and incident response defensibly, without a GRC platform or a team behind them.

## Before you rely on anything here

**This kit is designed to get a Department of One from nothing to something defensible, fast. It is a starting point, not a finished compliance program, and it is not designed to be bulletproof.**

- Every artefact here is deliberately simplified to be usable by one person with no budget and no compliance team behind them. Some choices are pragmatic defaults chosen for that context, not necessarily the most rigorous option a larger, better-resourced function would pick.
- Some content may diverge, intentionally or otherwise, from what a specific standard, framework, contract, or auditor expects. Every artefact ends with an **"Adapt this to your context"** section. Read it; the load-bearing caveats live there.
- Don't put anything here in front of an auditor, regulator, customer, or board as a certified or audit-ready control without reviewing and adapting it yourself first.
- Where a specific compliance program, contract, or regulator requires something stricter than what's written here, that requirement wins. Treat this kit as a floor to build from.

## Why this exists

A department of one still has to answer the same questions an enterprise IT function does: who has access to what, why, and who approved it. This kit is a from-scratch, generic answer to that, written for any solo operator to fork and adapt.

Every artefact here is written to stand on its own. If genericising something would leave nothing but a hollow shell, it isn't shipped at all.

## The documentation model

This kit, and its companion, [security-grc-kit](https://github.com/benguin5611/security-grc-kit), are organised by altitude and sponsorship. A single topic can span several layers:

| Layer | Altitude | Owned by | Answers |
|---|---|---|---|
| **Policies** | Strategic, deliberately generic | Executive-sponsored | Why does this function exist, and what does it commit to? |
| **Standards** | Tactical | IT/Security lead | Per-control directives, split into **Requirements** (must/shall) and **Guidelines** (should/may/can). |
| **Processes** | Implementation, changes often | The operator | The input to sub-process to output workflow, usually shown as a diagram. |
| **Procedures** | Implementation, changes often | The operator | The checklist for how one task inside a process actually gets done. |
| **Plans** | Implementation, invoked on a trigger | The operator | The pre-agreed playbook for a class of event. The incident response plan is one, filed under `processes/`. |
| **Registers** | Operational record | The operator | The listings that track value, location, ownership, and access. |
| **References** | Supporting material | | Templates and material that fit no other layer. |

Where a topic has both a cross-functional workflow and a hands-on checklist (joiners/movers/leavers, vendor onboarding), the two live in separate files under `processes/` and `procedures/` respectively, cross-linked to each other, rather than mixed together in one document.

ISO 27001 and an ISMS are one prominent use case for this taxonomy. It's a general-purpose way to structure any small function's documentation, with or without a certification in view.

## What's here

### Policies

| Artefact |
|---|
| [Information & Cyber Security Policy](policies/information-and-cyber-security-policy.md) |

### Standards

| Artefact |
|---|
| [Identity and Access Management Standard](standards/identity-and-access-management-standard.md) |
| [Endpoint Management and Protection Standard](standards/endpoint-management-and-protection-standard.md) |
| [Hardware Asset Management Standard](standards/hardware-asset-management-standard.md) |
| [OS Update Cadence Standard](standards/os-update-cadence-standard.md) |
| [Removable Media Standard](standards/removable-media-standard.md) |
| [Network and Cloud Security Standard](standards/network-and-cloud-security-standard.md) |
| [Domain Management Standard](standards/domain-management-standard.md) |
| [Information Classification and Handling Standard](standards/information-classification-and-handling-standard.md) |
| [Data Privacy and Record Protection Standard](standards/data-privacy-and-record-protection-standard.md) |
| [Vulnerability Management Standard](standards/vulnerability-management-standard.md) |
| [Acceptable Use Standard](standards/acceptable-use-standard.md) |
| [Remote and Flexible Work Standard](standards/remote-and-flexible-work-standard.md) |
| [Security Awareness and Training Standard](standards/security-training-standard.md) |
| [Change Management Standard](standards/change-management-standard.md) |

### Processes

| Artefact |
|---|
| [Cyber Security Incident Response Plan](processes/incident-response-plan.md) |
| [Joiners / Movers / Leavers processes](processes/joiners-movers-leavers/) |
| [Software Onboarding & Vendor Due Diligence process](processes/software-onboarding-vendor-due-diligence-process.md) |
| [Change Management Process](processes/change-management-process.md) |
| [Document Control Process](processes/document-control-process.md) |

### Procedures

| Artefact |
|---|
| [Joiners / Movers / Leavers procedures](procedures/joiners-movers-leavers/) |
| [Endpoint Privileged Access Management](procedures/endpoint-privileged-access-management-procedure.md) |
| [Access Management & Review](procedures/access-management-and-review-procedure.md) |
| [Software Onboarding & Vendor Due Diligence](procedures/software-onboarding-and-vendor-due-diligence-procedure.md) |
| [Password Reset & Identity Verification](procedures/password-reset-and-identity-verification-procedure.md) |

### Registers

| Artefact |
|---|
| [Company Asset Register](registers/company-asset-register.md) |
| [Policy and Documentation Register](registers/policy-and-documentation-register.md) |
| [Enterprise Risk Register](registers/enterprise-risk-register.md) |
| [Information Security Risk Register](registers/information-security-risk-register.md) |
| [Corrective Actions Register](registers/corrective-actions-register.md) |
| [Recurring Compliance Events Register](registers/recurring-compliance-events-register.md) |

### References

| Artefact |
|---|
| [Post-Incident Report Template](references/post-incident-report-template.md) |
| [Change Communication Guide](references/change-communication-guide.md) |
| [Vendor Due Diligence Questionnaire](references/vendor-due-diligence-questionnaire.md) |
| [Vendor Due Diligence Communication Template](references/vendor-due-diligence-communication-template.md) |

## Relationship to security-grc-kit

This kit and [security-grc-kit](https://github.com/benguin5611/security-grc-kit) are two halves of one documentation system, split by **audience**:

- **This kit**: a solo IT operator or department of one. Ships the operational checklist/template.
- **security-grc-kit**: a security/GRC practitioner. Ships the method/model/analysis behind it.

Where a topic touches both (vendor due diligence, risk, incident response, access review), this kit carries the operational checklist and register, and security-grc-kit carries the deeper method. Each side notes the other rather than forking the same content twice. For example, this kit's software onboarding procedure carries the operational vendor check, while security-grc-kit's third-party risk model carries the quantitative CIA times jurisdiction times adverse-history scoring behind it.

## Licensing

This subtree is **CC BY 4.0**: the licence text is in this directory's [LICENSE](LICENSE), and the repo root README's Licence section carries the dual-licensing note. The rest of this repository (the SBOM pipeline and LLM skills) stays **MIT**, which suits software better than a prose and template kit.
