# Security and privacy by design

Load in Phase 0 when the change touches data, identity, a network boundary or a destructive action;
the output is the gate template's Threats and privacy table. Proportionality governs everything here:
a three-endpoint tool gets a five-minute pass, a multi-party platform holding personal data gets the
full one.

## Pillars

Security is the architecture, not a layer: fail safely, authenticate explicitly, minimise at every
boundary. Privacy is a design constraint that improves quality. Clarity enables control: know what the
system does, touches and why. Minimisation defends against compromise: judge every field, feature and
role by its blast radius. Resilience is not optional: fail closed, degrade gracefully, recover
predictably; what you cannot observe you cannot secure. Developer experience is a control: secure by
default beats secure if configured.

## Controls to consider

Access: least privilege at every layer; separation of duties and multi-actor approval for
high-impact actions; authorisation checked at every entry point, never assumed done by another layer;
workflow-level control across a whole process; complete mediation on every request; tenant isolation
at every layer; short token lifetimes; expiring links and signed URLs; nothing persists indefinitely;
policy as code, tested; zero trust on identity and posture, not network. A self-declared answer (a mode
selector, a role picker) is not an authorisation decision: let it drive presentation, gate capability
on something checkable, and if a liar gains reach the answer was doing work it cannot support. Where
identity genuinely cannot be verified, choose provenance over prevention — stamp every action with the
declared mode and the authenticated account, keep withheld results, say plainly it is a policy
boundary. A declaration may narrow capability, never widen it.

Data: minimise and pseudonymise; consent as living, revocable state; data-subject rights as supported
operations; a lifecycle and destruction path for every dataset; encryption in transit, at rest, in
logs and backups; secrets from a runtime vault, rotated, never hardcoded.

Architecture: defence in depth with validation at the last enforcement point; minimal attack surface,
dormant endpoints retired; fail closed on missing context or error; secure defaults (auth required,
zero-access roles, deny-all, personal data out of logs); abuse cases in planning; immutable
infrastructure and configuration as code; compartmentalise to bound blast radius; partition async
work per tenant where multi-tenant; allowlist schemas, reject the rest.

Operations: structured tenant-aware logs free of secrets and personal data; no silent failure — every
error visible and alertable; privileged actions traceable in append-only storage; rate limits and
concurrency caps as guardrails at scale. Every skipped control is an explicit, recorded trade-off,
never a silent omission.

## Privacy principles

Attributed to Cavoukian's seven foundational principles, reworded: proactive not reactive; privacy
as the default — if the individual does nothing their privacy still holds (purpose specification,
collection limitation, minimisation, use and retention limits, the precautionary default); privacy
embedded in the design, with impact and risk assessment; positive-sum — treat an apparent trade-off as
a design problem; end-to-end lifecycle security including destruction; visibility and transparency
with a named owner and redress; user-centric defaults, notice and controls. The operational controls:
justify every personal-data field at design time; pseudonymise in logs, analytics and exports;
granular revocable consent tracked as state; access, rectification, erasure, portability and
restriction as first-class operations; retention limits; no personal data in telemetry by default,
enforced by field tagging not vigilance; a privacy impact assessment recorded as a decision for any
significant new use.

## The method

1. Inventory the personal data the change touches, why, and for how long; the cheapest data to
   protect is the data never held.
2. Model threats with a STRIDE pass sized to the change — as code where a tool exists, as a table
   otherwise — and abuse cases from the OWASP Top 10 lists and the CWE/CAPEC/ATT&CK catalogues.
3. Walk the controls above against the design, premise-checking each: name the failure it prevents
   and confirm it can occur here. Record what applies and what is deliberately skipped, with a
   decision reference.
4. Gate: every high or critical threat has a disposition row in the discovery artefact; personal-data
   risks are addressed or explicitly accepted; the no-personal-data-in-logs check is in the gate
   commands.
