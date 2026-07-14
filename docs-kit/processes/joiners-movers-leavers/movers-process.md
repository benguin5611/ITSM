---
Artefact type: Process
Owner role: IT operator
Review cadence: Annual, or on material tooling change
Version: 1.0 (template)
---

# Movers (role change) process

> Part of the [docs-kit](../../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer before relying on it.

The end-to-end workflow for a role change, from the HR system update through to closing the ticket. The [Movers procedure](../../procedures/joiners-movers-leavers/movers.md) is the detailed access-diff checklist that sits inside it.

```mermaid
flowchart TD
    A[Employee changes role] --> B[Role title updated in HR system]
    B --> C[Role-change ticket submitted]
    C --> D[Review role-based access profile for new role]
    D --> E{Moving to a new role type?}
    E -->|Yes| P[Line manager approves the access change] --> F[Revoke unnecessary access] --> G[Provision newly required access] --> H[Update group memberships]
    E -->|No| I{Documentation update required?}
    H --> I
    I -->|Yes| J[Update governance documentation]
    I -->|No| K[Confirm with user & line manager that access is sufficient]
    J --> K
    K --> L[Close ticket]
```

## Adapt this to your context

- A solo operator is often both the approver and the person making the change. Document the approval step anyway, even as a dated self-note, so the decision is reviewable later rather than only rememberable.
