---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# OS update cadence standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, rather than a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard defines how operating system updates (security patches, feature updates, and emergency out-of-band fixes) are rolled out across company-owned and BYOD devices. It balances two competing risks: unpatched devices are exploitable, but pushing every update immediately can break critical tooling and cost a day of productivity fleet-wide.

### Risks

Failing to implement this standard can expose the organisation to:

- Known vulnerabilities left unpatched and exploited before users update voluntarily
- A rushed major OS upgrade breaking business-critical tooling across the fleet
- Inconsistent enforcement, leaving some devices patched and others not
- Users caught by surprise when an update forces a restart mid-task
- No record of who was notified or when, complicating later incident review

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| OSU-100 | Enrol every company-owned device in a tool capable of enforcing OS update compliance automatically. |
| OSU-101 | Define and document a minimum supported OS version for each platform in the fleet. |
| OSU-102 | Bring devices to the minimum supported OS version by an enforced deadline; automatically update or restart devices that haven't updated by then. |
| OSU-103 | Enforce emergency/out-of-band security patches on a shorter deadline than routine updates. |
| OSU-104 | Notify users of a pending mandatory update and its enforcement deadline before enforcement occurs. |
| OSU-105 | Restrict devices that fall below the minimum supported OS version after the deadline from accessing company resources until compliant. |
| OSU-106 | Require personally-owned (BYOD) devices to meet the same minimum OS version bar before being granted access to company resources. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| OSU-200 | Hold major OS version upgrades back on a delay if there's a history of critical tooling breaking on major version bumps; validate the new version on a non-critical device before wide rollout. |
| OSU-201 | Send a staged sequence of reminders (initial notice, mid-point nudge, final warning) ahead of an enforcement deadline rather than a single notice. |
| OSU-202 | Skip intermediate reminders when the rollout window is short enough that users are expected to update well ahead of the deadline anyway. |
| OSU-203 | Shift reminder timing away from weekends and non-working days so it lands when people are actually working. |
| OSU-204 | Revisit minimum-supported-OS-version baselines on a recurring basis rather than leaving them static indefinitely. |
| OSU-205 | Point users to a troubleshooting reference for common post-update issues before they raise a support ticket. |
| OSU-206 | Schedule mandatory enforcement outside business-critical hours to reduce disruption. |
| OSU-207 | Confirm an update is actually available/cached on devices before notifying users, so the message matches reality. |

## Adapt this to your context

- Enforcement deadlines (7 days is a common starting point) should flex with your risk tolerance and how disruptive a forced restart is for your team's work patterns.
- If you support platforms unevenly (e.g. mostly one desktop OS, a handful of mobile devices), scale tooling and communication effort to match. A single-platform shop doesn't need per-OS messaging templates.
- The "hold back major upgrades" guideline (OSU-200) matters most if you depend on tooling with a track record of breaking on major version bumps; if your stack is mainstream vendor software only, you can likely adopt major versions faster.
- Tie enforcement to whatever identity or access-control tooling you already use, rather than standing up new tooling solely for this control.

**Frameworks referenced**: ISO/IEC 27001 Annex A, CIS Controls
