---
Artefact type: Register
Owner role: IT operator
Review cadence: Continuous (updated as risks are identified, reassessed, or closed); formally reviewed quarterly
Version: 1.0 (template)
---

# Enterprise risk register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, rather than a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The whole-of-business risk list: financial, operational, strategic, reputational, and technology risk together, so leadership can see what could hurt the business and what's being done about it in one place, without piecing it together from memory.

## Columns

| Column | Purpose |
| --- | --- |
| Risk ID | A short reference so the risk can be cited consistently across reports and reviews. |
| Risk title | A short, specific name for the risk, specific enough that two different risks never share a title. |
| Category | The type of risk, e.g. Financial, Operational, Strategic, Reputational, Compliance, Technology. |
| Description | What the risk actually is and what could trigger it, written so someone outside the room understands it without extra context. |
| Risk owner | The person accountable for making sure the risk is actively managed, rather than only recorded. |
| Likelihood | How probable the risk is, on an agreed scale (e.g. Rare / Unlikely / Possible / Likely / Almost certain). |
| Impact | How severe the consequence would be if it occurred, on an agreed scale (e.g. Minor / Moderate / Major / Severe). |
| Overall rating | Likelihood and impact combined into a single rating, using whatever risk matrix your organisation has agreed to. |
| Treatment | What's actually being done about it: Accept, Mitigate, Transfer, or Avoid, with a one-line note on the specific action. |
| Status | Where the risk sits in its lifecycle: Identified, Being assessed, Being treated, Monitoring, or Closed. |
| Next review date | When this risk is next due to be reassessed. |

## Worked example

| Risk ID | Risk title | Category | Risk owner | Likelihood | Impact | Overall rating | Treatment | Status | Next review date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ERR-014 | Single logistics provider concentration | Operational | R. Osei (Ops Lead) | Possible | Major | High | Mitigate: qualify a second freight provider | Being treated | 2026-10-01 |
| ERR-015 | Sole IT operator, no backup coverage | Operational | M. Delacroix (Managing Director) | Likely | Major | High | Mitigate: cross-train a second staff member on critical procedures | Being assessed | 2026-08-15 |
| ERR-016 | Foreign-currency exposure on offshore supplier contracts | Financial | T. Vukovic (Finance Lead) | Possible | Moderate | Moderate | Accept: within board-approved tolerance, monitor quarterly | Monitoring | 2026-09-30 |
| ERR-017 | Pending data-residency legislation in a key market | Compliance | J. Alderton | Unlikely | Severe | High | Mitigate: engage legal counsel to assess exposure | Identified | 2026-08-01 |

## Adapt this to your context

- **Risk appetite and scales**: this template assumes you've already agreed a likelihood/impact scale and a risk matrix that turns the two into an overall rating. Without that agreement upfront, "Overall rating" becomes a guess that different reviewers fill in differently.
- **Size and maturity**: a sole operator or founder can genuinely hold this whole list in their head at first. The register earns its keep the moment a second person needs visibility into it, or a board or investor asks for evidence it exists.
- **Industry and jurisdiction**: what counts as a material enterprise risk varies hugely by sector. A regulated financial services business carries risks (e.g. capital adequacy, conduct risk) a small SaaS company never will, and vice versa.
- **Compliance program**: if you're pursuing ISO 27001 certification, keep this register distinct from the [Information Security Risk Register](information-security-risk-register.md); the ISMS scope needs its own, narrower risk view even where the two overlap.

**Frameworks referenced**: ISO 31000 enterprise risk management; the COSO Enterprise Risk Management framework
