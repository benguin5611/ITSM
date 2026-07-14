---
Artefact type: Process
Owner role: IT operator, with Information Security Manager sign-off for critical software
Review cadence: Annual
Version: 1.0 (template)
---

# Software onboarding and vendor due diligence process

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer before relying on it.

The end-to-end workflow for adding a new piece of software, from request through to onboarding. The [Software Onboarding & Vendor Due Diligence procedure](../procedures/software-onboarding-and-vendor-due-diligence-procedure.md) is the detailed checklist for each stage.

If your organisation is itself a service provider, adding a new vendor that will touch your customers' data usually carries its own notice obligation. Most data-processing agreements require telling affected customers before a new sub-processor goes live, not after. Skip that branch entirely if you have no customer data flowing through vendors.

```mermaid
flowchart TD
    A[Vendor onboarding request raised] --> B[Preliminary suitability check]
    B --> C["Classify criticality (CIA rating) & supply-chain tier"]
    C --> D{Critical software?}
    D -->|Yes| E[Send evaluation questionnaire or request certifications]
    D -->|No| F[Review available security documentation]
    E --> G[Review responses]
    G --> H{Further information required?}
    H -->|Yes| I[Request further information] --> G
    H -->|No| J[Attach documentation to the request]
    F --> J
    J --> K{Approved?}
    K -->|No| L[Document rationale & close the request]
    K -->|Yes| M[Add software & vendor to the asset register]
    M --> N{Will the vendor process your customers' data?}
    N -->|Yes| O["Notify affected customers of the new sub-processor (per your DPA's notice period)"] --> P[Confirm notice period has elapsed]
    N -->|No| Q[Set review cadence from the criticality & tier rating]
    P --> Q
    Q --> R{High criticality or Tier 1?}
    R -->|Yes| S[Review annually]
    R -->|No| T[Review as needed]
    S --> U[Onboard vendor]
    T --> U
```

## Adapt this to your context

- The customer-notice branch above only applies if you're a service provider with customer data flowing through vendors. What counts as adequate notice (how many days, what format) is set by your data-processing agreements, not this diagram: check what you've actually committed to before assuming a number.
