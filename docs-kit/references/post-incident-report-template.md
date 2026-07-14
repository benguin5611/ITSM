---
Artefact type: Reference
Owner role: Whoever ran the incident response, reviewed by the Information Security Manager
Review cadence: Per incident (this is a template, not a living document)
Version: 1.0 (template)
---

# Post-incident report (PIR) template

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

Companion to the [Incident Response Plan](../processes/incident-response-plan.md). Run one of these for every P1/P2 incident (see the plan for priority definitions), or whenever a customer or regulator specifically asks for one.

---

## Executive summary

Provide a concise summary of the incident: when it was detected, what the impact was, and how it was resolved.

*Example: On a given date, a configuration flag intended to restrict a beta feature to a subset of users was accidentally enabled for everyone, making an in-development UI element visible more broadly than intended. No sensitive data was exposed. The misconfiguration was identified within 30 minutes and access was restricted by rolling back the flag. A permanent fix was released the same day to enforce scoping in code rather than relying on the flag alone. No user reports or external impact were recorded.*

---

## Timeline

List the major events from detection to resolution, in order.

| Milestone | Date & time | Description |
| --- | --- | --- |
| Detection | | |
| Response | | |
| Containment | | |
| Fix deployed | | |

---

## Detection and prioritisation

Describe how the issue was identified, when it was escalated, and how it was prioritised (see the Incident Response Plan's priority matrix).

**Risk ratings** (adapt the scale to whatever your organisation already uses for risk scoring):

- Likelihood of occurrence:
- Likelihood of adverse impact:
- Impact severity:
- Overall risk rating:

---

## Response and containment

Explain the immediate actions taken to prevent further impact.

### Response teams

List the teams or individuals directly involved in managing the incident, and what each one did.

### Objective identification

State the primary response objectives clearly: what were you actually trying to achieve, in order of priority.

---

## Investigation and analysis

Detail the findings from root-cause investigation: what actually happened, and what allowed it to happen.

---

## Eradication and recovery

Describe the root-cause fix that resolved the issue for good, so it can't silently recur.

### Test cases

Evidence-based scenarios confirming the fix works as intended.

| Scenario | Condition | Expected result | Purpose |
| --- | --- | --- | --- |
| | | | |

---

## Communication

Document how the incident was communicated, internally and externally. Note who was briefed, when, and whether any customer- or regulator-facing communication was required (see the Incident Response Plan's communication section for the reporting-obligation triggers).

---

## Root cause analysis

Use a "5 Whys" style breakdown: each answer prompts the next "why", until you reach something you can actually fix.

1. **Why did the incident happen?**
2. **Why did that happen?**
3. **Why wasn't it caught earlier?**
4. **Why didn't existing controls catch it?**
5. **Why wasn't that control in place?**

---

## Lessons learned

### What went well

### What needs improvement

Any opportunity for improvement identified here should be raised as a corresponding corrective action. A PIR only closes the loop once a gap it identifies produces a tracked follow-up.

---

## Supporting documentation

Link everything relevant: bug/engineering tickets, help-desk tickets, pull requests, the incident ticket itself, and this document once finalised (for P1/P2 incidents).

## Adapt this to your context

- **Mandatory threshold**: this template assumes a PIR is run for P1/P2 incidents (see the Incident Response Plan). Some regulators or contracts require a formal PIR/root-cause analysis for any *reportable* incident regardless of internal priority. Check your obligations rather than relying on the priority threshold alone.
- **Risk-rating scale**: the "risk ratings" section assumes you already have a risk-scoring approach elsewhere in the organisation. Reuse that scale here rather than inventing a second one just for incidents.
- **Regulated data**: if the incident involved regulated data (health, financial, government), your jurisdiction may require specific fields or a specific notification annex beyond what's templated here.
