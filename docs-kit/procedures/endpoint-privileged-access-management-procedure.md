---
Artefact type: Procedure
Owner role: IT operator, with Information Security Manager approval for non-technical grants
Review cadence: Annual
Version: 1.0 (template)
---

# Endpoint privileged access management procedure

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

Local admin rights on a laptop are a different risk surface from admin rights on a system. This procedure covers the endpoint (the laptop itself); system-level privileged access is covered separately by [Access Management & Review](access-management-and-review-procedure.md).

## Granting access

### Technical personnel (engineers, IT, anyone whose job requires routine admin rights)

Admin privilege is auto-enforced on the device and automatically demoted back to standard user after a defined period (commonly same-day, e.g. 8 to 10 hours) rather than left standing indefinitely. This is the pattern most MDM/endpoint-privilege-management tools support directly: time-boxed elevation that resets itself, so nobody has to remember to revoke it.

### Non-technical personnel

1. The requester raises a ticket asking for admin permission.
2. The requester states the business purpose.
3. Approval must come from the Information Security Manager (or equivalent).
4. Once approved, add the user to your admin-elevation entitlement group (whatever your MDM or endpoint-privilege tool calls its equivalent grouping).
5. Sync/propagate the change through your MDM so it actually takes effect on the device.

## Removing access

1. Remove the user from the admin-elevation entitlement group once the justification is no longer current.
2. Sync/propagate the removal through your MDM.
3. Verify the device shows the user demoted back to standard privileges.

## Troubleshooting: elevation silently fails

**Symptom**: the endpoint-privilege tool's icon/prompt appears to do nothing when clicked; console or system logs show something like `Failed to get group membership for user [Full Name]`.

**Cause**: some elevation tools look the user up by their **full name** and match it strictly against the directory record's `RecordName`. Stock macOS lookups (`id`, `dsmemberutil`) resolve a full name through the `RealName` attribute, so the account looks healthy everywhere else; a tool matching on `RecordName` alone can't resolve it when the record only holds a `firstname.lastname` short username, and elevation fails silently. This is observed behaviour in specific tools rather than something vendors document, so confirm which attribute your tool matches on before applying the fix.

**Fix**: add the user's full name as an alias to their `RecordName` in the local directory service:

```
sudo dscl . -append /Users/<username> RecordName "<Full Name>"
```

Example:

```
sudo dscl . -append /Users/jane.smith RecordName "Jane Smith"
```

This is a small, non-obvious fix, but it's the kind of thing that costs a solo operator a genuinely frustrating hour the first time it happens and thirty seconds every time after. It's worth documenting once.

## Adapt this to your context

- **Auto-timeboxed technical-staff admin** is a risk-acceptance decision that deserves deliberate, documented sign-off. Some compliance regimes (particularly environments in scope for card-payment data) may require compensating controls around blanket technical-staff admin rights, or disallow the pattern outright. Check your applicable framework before adopting it wholesale.
- **Platform-specific**: the directory-service troubleshooting section is macOS-specific. Windows and Linux fleets will have their own equivalent identity-matching quirks in whatever privilege-elevation tool they run. The *pattern* (elevation tools matching on the wrong identifier) is worth checking for even if the specific fix doesn't carry over directly.
- **Size**: a solo operator is often also the Information Security Manager approving their own elevated-access requests. Document the approval anyway. It's what makes the decision auditable later.
