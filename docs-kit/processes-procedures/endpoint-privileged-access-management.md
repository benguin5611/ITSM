---
Artefact type: Procedure
Owner role: IT operator, with Information Security Manager approval for non-technical grants
Review cadence: Annual
Version: 1.0 (template)
---

# Endpoint privileged access management procedure

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here) — a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

Local admin rights on a laptop are a different risk surface from admin rights on a system — this procedure covers the endpoint (the laptop itself), not system-level privileged access, which is covered by [Access Management & Review](access-management-and-review.md).

## Granting access

### Technical personnel (engineers, IT, anyone whose job requires routine admin rights)

Admin privilege is auto-enforced on the device and automatically demoted back to standard user after a defined period (commonly same-day — e.g. 8–10 hours) rather than left standing indefinitely. This is the pattern most MDM/endpoint-privilege-management tools support directly: time-boxed elevation that resets itself, so nobody has to remember to revoke it.

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

**Cause**: many macOS privilege-elevation tools match a user by their **full name** in the directory service, not by their account username. In environments where the local username follows a `firstname.lastname` convention but the directory record's `RecordName` only has the short username, the tool can't resolve the group membership check, and elevation fails silently.

**Fix**: add the user's full name as an alias to their `RecordName` in the local directory service:

```
sudo dscl . -append /Users/<username> RecordName "<Full Name>"
```

Example:

```
sudo dscl . -append /Users/jane.smith RecordName "Jane Smith"
```

This is a small, non-obvious fix, but it's the kind of thing that costs a solo operator a genuinely frustrating hour the first time it happens and thirty seconds every time after — worth documenting once.

## Adapt this to your context

- **Auto-timeboxed technical-staff admin** is a risk-acceptance decision, not a neutral default. Some compliance regimes — particularly environments in scope for card-payment data — may require compensating controls around blanket technical-staff admin rights, or disallow the pattern outright. Check your applicable framework before adopting it wholesale.
- **Platform-specific**: the directory-service troubleshooting section is macOS-specific. Windows and Linux fleets will have their own equivalent identity-matching quirks in whatever privilege-elevation tool they run — the *pattern* (elevation tools matching on the wrong identifier) is worth checking for even if the specific fix isn't.
- **Size**: a solo operator is often also the Information Security Manager approving their own elevated-access requests. Document the approval anyway — it's what makes the decision auditable later.
