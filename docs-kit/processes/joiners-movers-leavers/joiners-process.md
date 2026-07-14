---
Artefact type: Process
Owner role: IT operator
Review cadence: Annual, or on material tooling change
Version: 1.0 (template)
---

# Joiners (onboarding) process

> Part of the [docs-kit](../../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer before relying on it.

This is the end-to-end workflow across every function involved: recruitment, HR, and IT, shown at the altitude a policy or standard operates at. The [Joiners procedure](../../procedures/joiners-movers-leavers/joiners.md) is the detailed IT and access checklist for one part of it. Some early steps (advertising a role, interviewing) sit outside a solo IT operator's remit and are shown only for context. The procedure's acceptance criteria pick up once an offer has been accepted.

```mermaid
flowchart TD
    A[Recruitment need identified] --> B[Write position description]
    B --> C[Advertise the role]
    C --> D[Screen & interview candidates]
    D --> E{Suitable candidate found?}
    E -->|No| D
    E -->|Yes| F[Confirm offer internally]
    F --> G[Send offer to candidate]
    G --> H{Offer accepted?}
    H -->|No| D
    H -->|Yes| I[Prepare contract, notify IT & HR]
    I --> J[Distribute contract to new starter]
    J --> K[Create employee profile in HR system]
    K --> L[Notify the new starter's manager]
    L --> M{New hardware needed?}
    M -->|Yes| N[Purchase new asset]
    M -->|No| O[Assign existing asset]
    N --> O
    O --> P[Raise IT onboarding request]
    P --> Q[Prepare hardware & system access]
    Q --> R[Create accounts]
    R --> S[Assign access per role profile]
    S --> T[Brief the new starter]
    T --> U[Close onboarding ticket]
    U --> V[Confirm payroll setup]
    V --> W[Finalise induction schedule]
    W --> X[Update org chart]
    X --> Y[Track probation check-ins & training]
    Y --> Z[Onboarding complete]
```

## Adapt this to your context

- A solo operator collapses several of these boxes (recruitment, HR, IT) into one person. The workflow still matters as a checklist of what has to happen and in what order, even when one person is doing all of it.
