# A06:2025 — Insecure Design

Insecure design is a broad category focusing on risks related to design and architectural flaws. It calls for more use of threat modeling, secure design patterns, and reference architectures. Unlike implementation bugs, insecure design cannot be fixed by a perfect implementation — the flaw is in the design itself.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-256 | Plaintext Storage of a Password |
| CWE-501 | Trust Boundary Violation |
| CWE-522 | Insufficiently Protected Credentials |
| CWE-602 | Client-Side Enforcement of Server-Side Security |
| CWE-656 | Reliance on Security Through Obscurity |
| CWE-799 | Improper Control of Interaction Frequency |
| CWE-841 | Improper Enforcement of Behavioral Workflow |

## Detection Patterns

### Missing Rate Limiting

Check sensitive endpoints for rate limiting:
```
grep -rn "rateLimit\|rate_limit\|throttle\|slowDown\|RateLimiter\|@throttle\|THROTTLE"
```

Endpoints that MUST have rate limiting:
- Login / authentication
- Password reset / forgot password
- OTP / verification code submission
- Payment / checkout
- Account creation / registration
- API endpoints with expensive operations

If no rate limiting is found in the codebase, flag as High severity.

### Client-Side Security Enforcement

Look for security decisions made only on the client:

```
grep -rn "isAdmin\|isAuthorized\|canAccess\|hasPermission\|role ==" --include="*.jsx" --include="*.tsx" --include="*.vue" --include="*.svelte"
```

Vulnerable:
```jsx
// Client-only check — easily bypassed
{user.isAdmin && <AdminPanel />}
// API call without server-side authorization
fetch('/api/admin/users');
```

Every client-side authorization check must have a corresponding server-side check.

### Business Logic Abuse

**Negative quantity / amount:**
```
grep -rn "quantity\|amount\|price\|total\|balance" --include="*.ts" --include="*.js" --include="*.py"
```
Check that quantities, amounts, and prices are validated as positive numbers server-side.

**Race conditions on balances / inventory:**
Look for read-then-write patterns without locking:
```
grep -rn "balance\|inventory\|stock\|credits\|points"
```

Vulnerable:
```python
user = User.objects.get(id=user_id)
if user.balance >= amount:
    user.balance -= amount  # Race condition: two concurrent requests can both pass the check
    user.save()
```
Secure:
```python
with transaction.atomic():
    user = User.objects.select_for_update().get(id=user_id)
    if user.balance >= amount:
        user.balance -= amount
        user.save()
```

**Workflow bypass:**
Check that multi-step processes enforce step ordering server-side:
- Can step 3 be reached without completing step 2?
- Can payment be skipped in a checkout flow?
- Can email verification be bypassed?

### Missing Input Validation Schemas

```
grep -rn "req\.body\|req\.query\|req\.params\|request\.json\|request\.form\|request\.args"
```

Check that input is validated with schemas (Joi, Zod, Pydantic, marshmallow, class-validator) before use:

Vulnerable:
```javascript
app.post('/api/orders', (req, res) => {
  const { items, address } = req.body; // No validation
  createOrder(items, address);
});
```
Secure:
```javascript
const OrderSchema = z.object({
  items: z.array(z.object({ id: z.string(), quantity: z.number().positive() })),
  address: z.string().min(1).max(500),
});

app.post('/api/orders', (req, res) => {
  const data = OrderSchema.parse(req.body);
  createOrder(data.items, data.address);
});
```

### Missing CAPTCHA

Public-facing forms that should have CAPTCHA or equivalent bot protection:
- Registration
- Contact / feedback forms
- Password reset requests
- Public comment submission

### Enumeration Attacks

Check that responses don't reveal whether a resource exists:

Vulnerable:
```javascript
// Reveals valid usernames
if (!user) return res.status(404).json({ error: 'User not found' });
if (!passwordMatch) return res.status(401).json({ error: 'Wrong password' });
```
Secure:
```javascript
// Constant response regardless of which part failed
if (!user || !passwordMatch) return res.status(401).json({ error: 'Invalid credentials' });
```

## Remediation Summary

| Issue | Fix |
|-------|-----|
| No rate limiting | Add rate limiting middleware to sensitive endpoints |
| Client-only authz | Mirror every client check with server-side enforcement |
| Race conditions | Use database-level locking or atomic operations |
| No input validation | Add schema validation at every API boundary |
| User enumeration | Use constant-time, identical responses for auth failures |
| Missing CAPTCHA | Add bot protection on public forms |

## False Positive Guidance

- Client-side authorization checks for UI rendering (hiding buttons) are fine IF server-side checks also exist
- Rate limiting may be handled at the infrastructure level (API gateway, CDN, load balancer) rather than in application code
- Some enumeration is acceptable for UX (e.g., "email already registered" on signup) — context matters
- Internal APIs behind authentication may have lighter rate limiting requirements
