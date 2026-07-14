---
Artefact type: Reference
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Change communication guide

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

A change that's approved, tested, and rolled back safely can still cause a bad day for the people it affects, if they never heard about it. This guide sets out who to tell, when, and in what format, scaled to how much the change actually affects people, rather than a single fixed announcement process for everything.

## Match the message to the risk tier

| Risk tier | Advance notice | Audience | Channel | Must include |
| --- | --- | --- | --- | --- |
| Low: no visible impact | None required | Change record only | None | None |
| Standard: routine, brief or no visible impact | Same day or next business day | Directly affected users/teams | Team chat or email | What changed, who to contact if something looks wrong |
| Elevated: visible impact, no downtime | A few days ahead | All directly affected users and their team leads | Email + team chat | What's changing, when, what to expect, who to contact |
| High: affects availability, requires downtime, or touches authentication/access | At least a week ahead, with a reminder closer to the date | All affected users, plus the support/helpdesk function and, if customer-facing, leadership | Email + team chat + a durable reference page | What's changing, the exact window, expected impact, the rollback/contingency plan, who to contact, and what to do if something breaks |

## What a message needs to answer

Whatever the channel, a change announcement should answer, in plain language:

- **Who** is affected, and who is the right person to deliver the message so it lands with credibility.
- **What** is actually changing, and what is staying the same.
- **When** it happens, including any preparation window and hard deadlines.
- **Where** it applies: don't leave people to guess whether it covers their team, region, or system.
- **Why** it's happening: link it to a concrete benefit or problem being solved, not just "policy."
- **How** it will be rolled out, what's expected of the recipient, and where to get help.

For a low-risk change, "what," "when," and "how" alone may be enough. For anything touching availability or access, work through all six.

## Example announcement

> **Subject:** [System] will be briefly unavailable on [date]
>
> On [date] between [start time] and [end time], [system] will be unavailable while we [one-line description of the change and why]. No action is required from you beforehand. If you notice anything unexpected afterwards, contact [support channel/contact]. Thanks for your patience.

For higher-risk changes, add a short follow-up cadence: a heads-up a week or more out, a reminder the day before, the go-live message itself, and a brief close-out once the change has bedded in and any issues have been resolved.

## Adapt this to your context

- In a one-person operation, the person who approves the change and the person who announces it are the same individual. That's fine, but say so plainly rather than implying a committee that doesn't exist.
- Keep one plain-language message template as your default; only add a multi-stage before/during/after cadence once a change is complex or high-risk enough to need it.
- Keep a simple running log of what was announced, to whom, and when. If something goes wrong, you'll want to show what people were actually told.
