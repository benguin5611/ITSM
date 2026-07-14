---
Artefact type: Register
Owner role: IT operator
Review cadence: Continuous (checked whenever an event falls due); the calendar itself reviewed annually for completeness
Version: 1.0 (template)
---

# Recurring compliance events register

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The calendar of everything that has to happen on a schedule to keep a compliance program alive: access reviews, backup tests, management reviews, so cadence-based obligations don't quietly slip because nobody's job was to remember them.

## Columns

| Column | Purpose |
| --- | --- |
| Event ID | A short reference so the event can be cited consistently. |
| Event name | What the recurring obligation actually is. |
| Frequency | How often it recurs (e.g. Monthly, Quarterly, Semi-annual, Annual, or Ad hoc/triggered). |
| Owner | The person accountable for making sure it actually happens, not just for doing it once. |
| Last completed | The date it was last carried out. |
| Next due | The date it's next due, calculated from the frequency and last-completed date. |
| Evidence | What proves it happened: a signed report, a closed ticket, a log export, a meeting record. Only the artefact itself counts as evidence. |
| Status | On track, Due soon, Overdue, or Completed for this cycle. |

## Worked example

| Event ID | Event name | Frequency | Owner | Last completed | Next due | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RCE-005 | Access review, all in-scope systems | Quarterly | J. Alderton | 2026-04-15 | 2026-07-15 | Signed access review sheet, filed with the review | Due soon |
| RCE-006 | Management review of the security program | Annual | M. Delacroix | 2025-11-01 | 2026-11-01 | Meeting minutes and action list | On track |
| RCE-007 | Backup restore test | Semi-annual | S. Nakamura | 2026-01-20 | 2026-07-20 | Restore test log and outcome summary | Due soon |
| RCE-008 | Annual review of the policy and documentation library | Annual | J. Alderton | 2025-06-30 | 2026-06-30 | Updated Policy and Documentation Register with new review dates | Overdue |

## Adapt this to your context

- **Frequency drift**: a recurring event completed a few days late every cycle will eventually drift a full quarter off schedule. Set "Next due" from the frequency and the *original* schedule, not from whenever it last actually happened, or the whole calendar slowly slips.
- **Size and maturity**: a sole operator can run this as a personal calendar with reminders at first. It earns its place as a proper register the moment someone else needs to see what's due, or an auditor asks for evidence a given event has actually recurred on schedule.
- **Compliance program**: the specific list of recurring events depends entirely on what you're certified against or contractually committed to. A fresh ISO 27001 program and a mature SOC 2 Type II program will have materially different calendars.
- **Ad hoc-triggered events**: not everything recurs on a fixed clock. Some obligations trigger off an event (e.g. a new supplier onboarding requiring a due-diligence review). Track those here too, with "Frequency" set to Ad hoc/triggered, rather than only tracking calendar-based cadences.

**Frameworks referenced**: ISO/IEC 27001's internal audit, management review, and continual improvement requirements; SOC 2's ongoing monitoring criteria
