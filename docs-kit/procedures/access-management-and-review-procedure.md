---
Artefact type: Procedure
Owner role: IT operator, with System Owner and (for privileged access) Information Security Manager approval
Review cadence: Annual for standard access; quarterly for privileged access on critical systems
Version: 1.0 (template)
---

# Access management & review procedure

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

Covers granting, removing, and periodically reviewing system access: standard and privileged. Endpoint (laptop) admin rights specifically are covered separately by [Endpoint Privileged Access Management](endpoint-privileged-access-management-procedure.md); this procedure is about access to *systems*.

## Granting standard access

1. The requester raises a ticket asking for system access.
2. The requester states the business purpose.
3. Get approval from the requester's line manager **and** the system owner.
4. If approved:
   1. Ask the system owner (or whoever administers the system) to provision the access.
   2. Provide the password via out-of-band methods if self-service password reset isn't available.
   3. Require the password to be changed on first login, if the system supports it.
   4. Record the granted access in the [Company Asset Register](../registers/company-asset-register.md).
   5. Tell the requester the access is live.
5. If rejected, tell the requester and record why.

## Granting privileged access

Same shape as standard access, with two differences that reflect the higher blast radius:

1. Approval must come from the **Information Security Manager** (or equivalent) **and** the system owner, not just a line manager.
2. **If the need is temporary, set an expiry date on the account at the time it's created.** Don't rely on remembering to revoke it later. An access grant with no natural end date is the single most common way privileged access outlives its justification.

Everything else (out-of-band password delivery, forced change on first login, recording the grant in the asset register) applies the same way.

## Removing access (standard or privileged)

1. Raise a ticket to remove the access.
2. Ask the system owner (or administrator) to remove it.
3. Update the [Company Asset Register](../registers/company-asset-register.md) to reflect the removal.

## Periodic review

Access that's never reviewed drifts: people move roles, projects end, temporary grants quietly become permanent. Review on a fixed cadence, not "whenever it comes to mind":

- **Standard access**: review every system at least every **12 months**. Confirm every account and user ID is documented, only authorised users hold an account, and unused licences are revoked. Keep evidence of the review for audit purposes.
- **Privileged access on critical systems**: review at least every **3 months**. Confirm only authorised users hold a privileged account, and that the justification for each still holds. Keep evidence of the review for audit purposes.

The full set of underlying requirements this review cadence is drawn from (including password/authentication requirements and the account-inventory discipline that makes a review actually possible to run) lives in the [Identity and Access Management Standard](../standards/identity-and-access-management-standard.md).

## Adapt this to your context

- **Review cadence**: 12 months (standard) and 3 months (privileged, critical systems) are common baselines, not a universal floor. Some frameworks, regulators, or specific contracts require shorter cycles, including for *all* access rather than just privileged access. Check what actually applies before relying on these figures.
- **Approval chain**: line manager + system owner (standard), or Information Security Manager + system owner (privileged), assumes those roles exist as separate people. A solo operator collapses this to a documented self-approval. Add a compensating control (e.g. a periodic external or peer review of the approval log) rather than dropping the step silently.
- **Industry**: regulated sectors may require the review itself to be independently verified (not just performed and logged). Check whether self-attestation is sufficient for your compliance program or whether it needs a second set of eyes.

**Frameworks referenced**: ISO/IEC 27001:2022 Annex A's access-related controls; NIST's access-control guidance (SP 800-53 family) if you operate in or alongside a US government context.
