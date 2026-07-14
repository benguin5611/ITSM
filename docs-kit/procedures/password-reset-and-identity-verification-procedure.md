---
Artefact type: Procedure
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Password reset & identity verification procedure

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The workflow that stops a password reset from becoming a social-engineering hole. Almost none of this is employer-specific. It's close to universally applicable, and it's the single highest-value procedure in this kit relative to how short it is.

## Self-service first

1. Encourage self-service password reset wherever it's available.
2. Point the user to the right self-service tool.
3. Only move to a manual reset once self-service has genuinely been exhausted.

## Manual reset

1. The user raises a request through the help desk (or however requests get routed).
2. **Verify identity before doing anything else.** Proceed with the reset only after verification succeeds.

### Identity verification workflow

- **In person, whenever possible.** This is the strongest verification available and costs nothing extra when the person is physically reachable.
- **Remote, when in-person isn't feasible**: verbal confirmation over phone, video call, or instant messaging.
  - Ask for agreed vital-statistic information (e.g. device serial number, employee ID, or another identifier set up in advance) plus a second pre-agreed identifier (e.g. a verification phrase) as a second factor.
  - Confirm what's given matches the records on file.
  - The whole point of this step is that "I say I'm Jane" is not identity verification. An attacker who knows someone's name and job title can say that too. The vital-statistic questions exist specifically to filter that out.

### Resetting the password

1. Generate a strong, unique password.
2. Use a one-time password where the system supports it, and require the user to change it.
3. Provide the password via an out-of-band channel.
4. Require a forced change on next login, if the system supports it.
5. Tell the user to change it immediately after reset to a personal, strong password of their own choosing.
6. Don't schedule any further rotation; force a change only on evidence or suspicion of compromise.

## Documentation

Document the reset (including the identity verification method used and the date/time) for audit purposes. Close the request once done.

## Adapt this to your context

- **Rotation policy**: the "generate a strong password, no mandatory rotation" stance reflects current digital-identity best practice, but some older frameworks, specific auditors, or contractual requirements still expect periodic rotation regardless. Confirm what actually applies to you before assuming rotation is unnecessary.
- **Vital-statistic questions**: whatever you choose as the "agreed identifier" for remote verification must genuinely be hard to find publicly: nothing discoverable via social media, a company directory, or a prior data breach. Revisit your chosen identifiers periodically as public-information norms shift.
- **Size**: a solo operator doing in-person verification is verifying someone they likely already know by sight; that familiarity is a feature worth keeping, but the step should still be logged.

**Frameworks referenced**: NIST's digital identity guidelines (SP 800-63 series).
