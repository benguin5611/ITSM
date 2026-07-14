---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Change management standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard sets the baseline for how changes to information systems, applications, infrastructure, and operational processes are requested, assessed, approved, implemented, and reviewed. It exists to stop unauthorised, untested, or poorly understood changes from reaching production, while keeping the approval overhead proportionate to how much risk a given change actually carries. It applies to any change made by staff, contractors, or vendors that could affect the confidentiality, integrity, or availability of information assets.

### Risks

Without a working change management control, an organisation is exposed to:

- Unauthorised or unplanned changes reaching production undetected.
- New security vulnerabilities introduced by unreviewed changes.
- Outages or degraded service caused by untested changes.
- Data exposure or loss triggered by a change whose impact was never properly assessed.
- Difficulty demonstrating change control to auditors, customers, or regulators who require it.
- A process so heavy-handed or slow that people quietly route around it, which defeats the purpose entirely.

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| CHG-100 | Establish and document an approval path for changes that materially affect the functionality, performance, security, or availability of an information system. |
| CHG-101 | Assess every change for its potential impact on confidentiality, integrity, and availability before it is approved. |
| CHG-102 | Record, for every change, the reason for the change, what is changing, and the risks identified, in a standard change record. |
| CHG-103 | Involve relevant stakeholders (including whoever is accountable for security) in planning and approving changes above the low-risk threshold. |
| CHG-104 | Maintain a record of planned and completed changes, including their timelines, sufficient to reconstruct what changed and when. |
| CHG-105 | Classify each change into a risk tier and route it through the approval path defined for that tier. |
| CHG-106 | Use a structured, repeatable process to implement changes, including defined testing and validation steps. |
| CHG-107 | Assess the impact of a change on existing security controls, and put compensating controls in place where a gap is identified. |
| CHG-108 | Maintain a rollback plan, agreed before implementation, capable of reverting the change if it causes unexpected issues. |
| CHG-109 | Test and validate changes in an environment separate from production before deployment, proportionate to the change's risk. |
| CHG-110 | Assign a single accountable owner to every change, responsible for its outcome from request through to closure. |
| CHG-111 | Document emergency changes that bypass the normal approval path retrospectively (including justification, risk assessment, and impact) within a fixed, short window after implementation. |
| CHG-112 | Have emergency changes formally reviewed and approved after the fact by whoever holds ultimate accountability for security and technology risk. |
| CHG-113 | Block a change from proceeding to implementation until both testing and a rollback plan are in place. |
| CHG-114 | Keep change requester, approver, and implementer as distinct roles wherever team size allows, so no single person controls a change end to end unchecked. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| CHG-200 | Conduct a post-implementation review after each change to confirm it achieved its intended outcome and capture any lessons learned. |
| CHG-201 | Produce periodic change management reporting for leadership, covering volume, success rate, and any incidents traced back to change. |
| CHG-202 | Declare change-freeze periods around high-risk windows (audits, major launches, period-end close) during which only emergency changes are permitted. |
| CHG-203 | Communicate change-freeze periods in advance, and route any exception through the emergency change path. |
| CHG-204 | Maintain a forward-looking change calendar so overlapping or conflicting changes can be identified before they collide. |
| CHG-205 | Review the change management process itself at a regular interval and adjust risk tiers, approval paths, or record-keeping based on what's actually happening in practice. |
| CHG-206 | Use automated deployment and testing pipelines where practical, to reduce the manual effort and error rate of routine changes. |
| CHG-207 | Record a brief retrospective on any failed or rolled-back change, distinct from routine post-implementation review, to capture specifically what went wrong. |
| CHG-208 | Make the change record and its approval history visible to anyone affected by the change, not only to the approvers. |
| CHG-209 | Handle communication of a change to its stakeholders as a separate practice (see the [Change Communication Guide](../references/change-communication-guide.md)), rather than treating the change record itself as the announcement. |
| CHG-210 | Periodically sample closed changes to confirm the process was actually followed, not just documented as followed. |
| CHG-211 | Extend a lighter-touch version of this process to vendor- or third-party-initiated changes that affect your environment, so they don't bypass risk assessment entirely. |

## Adapt this to your context

- A one-person team can satisfy the intent of "distinct requester/approver/implementer" by writing the change down before doing it and setting a plain risk threshold (for example, anything touching customer data, external access, or authentication) above which you deliberately seek a second opinion from a peer, contractor, or advisor.
- Growing teams should replace self-attestation with genuine second-person approval, and stand up a lightweight change advisory function once change volume or risk makes a single approver a bottleneck.
- Don't build ten risk tiers you'll never populate: three (for example, low/medium/high) is enough to start; subdivide later once real data tells you where the tiers are actually straining.

**Frameworks referenced**: ISO/IEC 27001:2022 (Annex A control 8.32, Change management), ITIL (change enablement practice)
