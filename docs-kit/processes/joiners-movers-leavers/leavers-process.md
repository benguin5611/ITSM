---
Artefact type: Process
Owner role: IT operator
Review cadence: Annual, or on material tooling change
Version: 1.0 (template)
---

# Leavers (offboarding) process

> Part of the [docs-kit](../../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer before relying on it.

The end-to-end workflow spanning payroll, HR, and IT. The [Leavers procedure](../../procedures/joiners-movers-leavers/leavers.md) is the IT-execution slice of it: the steps a solo operator actually runs.

```mermaid
flowchart TD
    A[Resignation / termination received] --> B[Notify payroll]
    B --> C[Confirm leave & entitlement position]
    C --> D[Follow up outstanding leave]
    D --> E[Prepare confirmation of resignation / end of employment]
    E --> F[Send exit checklist to employee]
    F --> G[Schedule exit interview]
    G --> H[Set off-boarding date in HR system]
    H --> I[Complete exit interview]
    I --> J[Arrange return of assets on/before last day]
    J --> K[Raise IT off-boarding ticket]
    K --> L["Exit user from systems before close of business, last day"]
    L --> M{All assets returned?}
    M -->|No| N[Escalate to line manager] --> O[Arrange asset retrieval] --> P[Return assets to office]
    M -->|Yes| Q[Prepare assets for re-use: wipe, etc.]
    P --> Q
    Q --> R{Documentation update required?}
    R -->|Yes| S[Update governance documentation]
    R -->|No| T[Close IT off-boarding ticket]
    S --> T
    T --> U[Communicate departure to staff]
    U --> V[Off-boarding complete]
```

The value in the linked procedure is the order of operations and the timing rules, not the click-path through any particular identity provider's admin console. Whatever your stack is, that sequence is what keeps a departure from leaving an open door behind.

## Adapt this to your context

- A solo operator runs every box in this diagram personally. Naming the steps still matters: it's what a stand-in or successor would need to follow if you were unavailable when someone left.
