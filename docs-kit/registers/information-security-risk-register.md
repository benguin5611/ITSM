---
Artefact type: Register
Owner role: IT/Security lead
Review cadence: Continuous (updated as risks are identified, assessed, or treated); formally reviewed at least quarterly, with a full reassessment annually
Version: 1.0 (template)
---

# Information security risk register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, rather than a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The narrower, ISMS-scoped sibling of the [Enterprise Risk Register](enterprise-risk-register.md): every risk to the confidentiality, integrity, or availability of information and the systems that hold it, tracked from identification through to treatment and ongoing monitoring.

## Columns

| Column | Purpose |
| --- | --- |
| Risk ID | A short reference so the risk can be cited consistently in audits, reviews, and reports. |
| Risk title | A short, specific description of the risk. |
| Category | The information security domain it falls under, e.g. Access control, Third-party/supplier, Malware, Data protection, Physical, Business continuity. |
| Description | The threat and vulnerability combination that creates the risk, and what asset or system it affects. |
| Affected asset(s) | The system, data set, or asset the risk relates to, cross-referenced to the [Company Asset Register](company-asset-register.md) where possible. |
| Likelihood | How probable the risk is, on an agreed scale. |
| Impact | How severe the consequence would be, on an agreed scale. |
| Inherent rating | Likelihood combined with impact, before any treatment is applied. |
| Related control(s) | Which control(s) (e.g. an ISO 27001 Annex A control or a SOC 2 criterion) this risk maps to, if you're tracking against a specific control framework. |
| Treatment | Accept, Mitigate, Transfer, or Avoid, with a one-line note on the specific action. |
| Risk owner | The person accountable for the risk being actively managed. |
| Status | Identified, Being assessed, Being treated, Monitoring, or Closed. |
| Next review date | When this risk is next due to be reassessed. |

## Worked example

| Risk ID | Risk title | Category | Affected asset(s) | Inherent rating | Related control(s) | Treatment | Owner | Status | Next review date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ISR-021 | Field laptops back up to an unencrypted external drive | Data protection | Field laptop fleet | High | Cryptography / data protection controls | Mitigate: enforce full-disk encryption, move backups to an encrypted managed target | S. Nakamura | Being treated | 2026-09-01 |
| ISR-022 | Shared admin credential used across three systems | Access control | Orbit CRM, Vault Payroll, Nimbus File Share | High | Access control / privileged access controls | Mitigate: move to named admin accounts with MFA | J. Alderton | Identified | 2026-08-10 |
| ISR-023 | Support vendor holds standing access to production data | Third-party/supplier | Nimbus File Share | High | Supplier relationship controls | Mitigate: restrict to time-boxed, ticket-triggered access | J. Alderton | Being assessed | 2026-08-20 |
| ISR-024 | No tested restore from backup in over 12 months | Business continuity | Core file storage | Moderate | Business continuity / backup controls | Mitigate: schedule a quarterly restore test | S. Nakamura | Monitoring | 2026-10-01 |

## Adapt this to your context

- **Where the scoring comes from**: this register is where assessed risks *live*, separate from the method for scoring them. You need an agreed likelihood/impact scale and a consistent way of applying it before "Inherent rating" means the same thing across every row; the companion [security-grc-kit](https://github.com/benguin5611/security-grc-kit) carries a worked risk-assessment method for exactly that, if you don't already have one.
- **Control framework alignment**: leave "Related control(s)" blank if you're not yet mapping risks to a specific framework. Forcing a mapping before you've adopted one just produces noise.
- **Size and maturity**: a solo operator can start this the day they identify their first real information security risk. Don't wait for a formal ISMS project to begin tracking what you already know.
- **Compliance program**: if you're pursuing ISO 27001 certification, this register (and its treatment decisions) is exactly what an auditor expects to see evidence of. Keep your Statement of Applicability's control justifications consistent with what's recorded here.

**Frameworks referenced**: ISO/IEC 27001's risk assessment and risk treatment requirements; SOC 2's risk assessment criteria
