# A07:2025 — Authentication Failures

Authentication failures allow attackers to compromise passwords, keys, or session tokens, or to exploit implementation flaws to assume other users' identities temporarily or permanently.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-287 | Improper Authentication |
| CWE-307 | Improper Restriction of Excessive Authentication Attempts |
| CWE-308 | Use of Single-factor Authentication |
| CWE-384 | Session Fixation |
| CWE-521 | Weak Password Requirements |
| CWE-613 | Insufficient Session Expiration |
| CWE-640 | Weak Password Recovery Mechanism for Forgotten Password |
| CWE-798 | Use of Hard-coded Credentials |

## Detection Patterns

### Password Storage

Grep patterns:
```
(?i)md5\(.*password|sha1\(.*password|sha256\(.*password
(?i)hashlib\.(md5|sha1|sha256).*password
(?i)MessageDigest.*password
(?i)password.*=.*encode\(|password.*=.*base64
```

**Weak hashing — all languages:**

Vulnerable:
```javascript
const hash = crypto.createHash('sha256').update(password).digest('hex');
```
Secure:
```javascript
const hash = await bcrypt.hash(password, 12);
// or
const hash = await argon2.hash(password, { type: argon2.argon2id });
```

**Bcrypt cost factor:**
```
grep -n "bcrypt\.\(hash\|genSalt\)"
```
Ensure cost factor is >= 10 (12 recommended). Flag `bcrypt.hash(password, 4)` or similar low values.

### JWT Vulnerabilities

Grep patterns:
```
alg.*none|algorithm.*none|algorithms.*\[.*none
jwt\.decode\(.*verify\s*=\s*False|jwt\.decode\(.*options.*ignoreExpiration
expiresIn|exp:|"exp"\s*:
jwt\.sign\(|jwt\.encode\(
```

**Missing expiration:**

Vulnerable:
```javascript
const token = jwt.sign({ userId: user.id }, secret);
```
Secure:
```javascript
const token = jwt.sign({ userId: user.id }, secret, { expiresIn: '1h' });
```

**Algorithm confusion:**

Vulnerable:
```javascript
const decoded = jwt.verify(token, publicKey, { algorithms: ['HS256', 'RS256', 'none'] });
```
Secure:
```javascript
const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] });
```

### Session Management

Grep patterns:
```
(?i)session.*localStorage|localStorage.*session|localStorage.*token
(?i)session.*cookie.*secure\s*:\s*false|httpOnly\s*:\s*false
(?i)session_id.*=.*req\.(query|url|params)
```

**Session in URL:**
Flag any pattern where session tokens appear in URLs or query parameters.

**Session fixation:**
Check that session IDs are regenerated after authentication:
```
grep -n "req\.session\.regenerate\|session\.cycle\|request\.session\.flush"
```
If login handlers exist without session regeneration, flag it.

**Cookie security flags:**

Vulnerable:
```javascript
res.cookie('session', token, { httpOnly: false, secure: false });
```
Secure:
```javascript
res.cookie('session', token, { httpOnly: true, secure: true, sameSite: 'strict' });
```

### Password Policy

Grep patterns:
```
(?i)minlength.*[1-7]\b|min_length.*[1-7]\b|password.*min.*[1-7]\b
(?i)password.*maxlength|password.*max_length
```

Flag password policies with:
- Minimum length < 8 characters
- Maximum length restrictions (should allow at least 64+ characters for passphrases)
- No complexity requirements at all

### Brute Force / Rate Limiting

Grep patterns for login endpoints:
```
(?i)/login|/signin|/authenticate|/auth/token
```

Check that login endpoints have:
- Rate limiting middleware
- Account lockout after N failed attempts
- CAPTCHA after repeated failures
- Exponential backoff

```
grep -n "rateLimit\|rate_limit\|throttle\|slowDown\|RateLimiter\|@throttle"
```

### Credential Exposure

Grep patterns:
```
(?i)console\.log.*password|print.*password|log\.(info|debug|warn).*password
(?i)console\.log.*token|print.*token|log\.(info|debug|warn).*secret
```

Flag any logging of passwords, tokens, or secrets even in debug-level logs.

### Multi-Factor Authentication

Look for authentication flows and check if MFA is supported:
- Is there a second factor verification step?
- Can MFA be bypassed by hitting the API directly?
- Are backup codes properly hashed and single-use?

## Remediation Summary

| Issue | Fix |
|-------|-----|
| Weak password hash | Use Argon2id or bcrypt (cost 12+) |
| JWT no expiration | Add `expiresIn` / `exp` claim |
| JWT algorithm none | Explicitly specify allowed algorithms |
| Session in localStorage | Use httpOnly secure cookies |
| No rate limiting on login | Add rate limiter middleware |
| No session regeneration | Regenerate session ID after login |
| Passwords in logs | Strip sensitive fields before logging |
| Weak password policy | Minimum 8 chars, check against breached passwords list |

## False Positive Guidance

- Test files with hardcoded passwords/tokens for test fixtures are expected
- OAuth/OIDC redirect flows legitimately pass tokens in URLs briefly — check for proper handling
- API keys for public/free services (e.g., public map tiles) may be acceptably hardcoded
- Password validation messages revealing policy requirements (not the password itself) are fine
- Session tokens in localStorage may be intentional for SPAs — flag but note tradeoff vs XSS risk
