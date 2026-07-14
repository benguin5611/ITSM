---
Artefact type: Register
Owner role: IT operator
Review cadence: Continuous (updated as actions are raised, progressed, or closed); triaged at least monthly so nothing stalls unnoticed
Version: 1.0 (template)
---

# Corrective actions register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

Every nonconformity, audit finding, or incident follow-up that needs a fix, tracked from root cause through to a verified, effective control, so "we'll get to it" doesn't quietly become "we forgot about it."

## Columns

| Column | Purpose |
| --- | --- |
| Action ID | A short reference so the action can be cited in audits, reports, and follow-up tickets. |
| Source | What raised the action: an internal audit, a security incident, a self-identified nonconformity, a customer complaint, or an external audit finding. |
| Description | What went wrong, in enough detail that someone outside the original incident understands the issue. |
| Root cause | Why it actually happened, not just what happened. A fix aimed at the wrong root cause won't stop it recurring. |
| Corrective action | What's being done to fix the underlying cause, not just the immediate symptom. |
| Owner | The person accountable for delivering the action. |
| Target date | When the action is due to be completed. |
| Status | Open, Investigating, Designing the control, Implementing, Verifying effectiveness, or Closed. |
| Verification | How and when effectiveness was checked, and what the outcome was. A corrective action isn't closed just because the task was done. |
| Related risk/control | A cross-reference to the risk or control this action relates to, if one exists. |

## Worked example

| Action ID | Source | Description | Root cause | Corrective action | Owner | Target date | Status | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA-009 | Internal review | No backup restore test performed in over 12 months | No recurring event existed to trigger the test | Add a quarterly restore test to the compliance calendar | S. Nakamura | 2026-08-01 | Implementing | Pending; retest scheduled 2026-09-01 |
| CA-010 | Security incident follow-up | A phishing email bypassed the mail filter and reached three staff | Filter rule set hadn't been updated since initial setup | Update filter rules; monitor for repeat bypass | J. Alderton | 2026-07-25 | Verifying effectiveness | Monitoring 30 days from 2026-07-20 |
| CA-011 | Self-identified nonconformity | A leaver's laptop wasn't wiped within the SLA | Offboarding checklist had no hard deadline | Add a wipe deadline and a checklist sign-off step | S. Nakamura | 2026-08-05 | Designing the control | N/A |
| CA-012 | External audit finding | Vendor risk assessments weren't refreshed on schedule | No owner assigned to the recurring review | Assign an owner; add the review to the recurring events calendar | M. Delacroix | 2026-07-30 | Closed | Verified 2026-07-28 |

## Adapt this to your context

- **Root cause discipline**: it's tempting to record the fix and skip the root cause, especially under time pressure. Resist it. An action closed without an honest root cause tends to recur, just with a different trigger next time.
- **Size and maturity**: a sole operator can run this as a flat list; once actions start coming from multiple sources (audits, incidents, complaints) at real volume, filter by "Source" rather than losing the thread across one long list.
- **Compliance program**: ISO 27001 and ISO 9001 both expect corrective actions tracked through to a verified, effective outcome, not just closed on completion. Check what evidence of "effectiveness" your specific certification expects before treating "task done" as the same thing as "closed."
- **Severity triage**: not every finding needs the same rigour. A minor documentation gap and a control failure that let real access occur don't belong on the same urgency, even if both pass through the same register.

**Frameworks referenced**: ISO/IEC 27001 and ISO 9001's corrective action and nonconformity requirements; SOC 2's control-deficiency remediation criteria
