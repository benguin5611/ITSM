# A09:2025 — Security Logging & Alerting Failures

Insufficient logging, monitoring, and alerting allow attackers to go undetected, maintain persistence, pivot to other systems, and tamper with or extract data. Without adequate logging, breaches cannot be detected or investigated.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-117 | Improper Output Neutralization for Logs (Log Injection) |
| CWE-223 | Omission of Security-relevant Information |
| CWE-532 | Insertion of Sensitive Information into Log File |
| CWE-778 | Insufficient Logging |

## Detection Patterns

### Sensitive Data in Logs

Grep patterns:
```
(?i)log\.\w+\(.*password|logger\.\w+\(.*password|console\.log\(.*password
(?i)log\.\w+\(.*token|logger\.\w+\(.*token|console\.log\(.*token
(?i)log\.\w+\(.*secret|logger\.\w+\(.*credit.card|console\.log\(.*ssn
(?i)log\.\w+\(.*req\.body|logger\.\w+\(.*request\.body
```

Flag logging of:
- Passwords or password hashes
- Session tokens, JWTs, API keys
- Credit card numbers, SSNs, PII
- Full request bodies (may contain sensitive fields)

Vulnerable:
```javascript
logger.info(`User login attempt: ${username}, password: ${password}`);
logger.debug('Request body:', req.body); // May contain sensitive fields
```
Secure:
```javascript
logger.info(`User login attempt: ${username}`);
logger.debug('Request body:', sanitizeForLogging(req.body));
```

### Missing Audit Logging

Events that MUST be logged:
- Authentication attempts (success and failure)
- Authorisation failures (access denied)
- Input validation failures
- Account changes (password reset, email change, role changes)
- Administrative actions
- Data access for sensitive records

Check authentication handlers:
```
grep -rn "login\|authenticate\|signIn" --include="*.ts" --include="*.js" --include="*.py" --include="*.java"
```

Look for logging statements near authentication logic. If none exist, flag as missing audit logging.

### Swallowed Exceptions

Grep patterns:
```
catch\s*\([^)]*\)\s*\{\s*\}
catch\s*\(\w+\)\s*\{\s*//
except\s*:\s*$|except\s+\w+:\s*$|except.*:\s*pass$
rescue\s*$|rescue\s*=>\s*\w+\s*$
```

Vulnerable:
```javascript
try { riskyOperation(); } catch (e) {} // Silently swallowed
try { riskyOperation(); } catch (e) { /* ignore */ }
```
Secure:
```javascript
try { riskyOperation(); } catch (e) { logger.error('Operation failed', { error: e.message, context }); }
```

### Log Injection

Grep patterns — user input directly in log messages:
```
(?i)log\.\w+\(.*req\.(params|query|body)\.\w+|logger\.\w+\(.*request\.(args|form)
console\.log\(.*\$\{req\.|logger\.info\(f".*\{request\.
```

Vulnerable:
```javascript
logger.info(`User searched for: ${req.query.search}`);
// Attacker injects: "search=test\n[ERROR] Admin logged in from 1.2.3.4"
```
Secure:
```javascript
logger.info('User search', { query: req.query.search }); // Structured logging escapes values
```

### Missing Structured Logging

Check for string-based logging vs structured:
```
grep -rn "console\.log\|print(\|System\.out\.print"
```

Vulnerable:
```python
print(f"Error processing order {order_id}: {error}")
```
Secure:
```python
logger.error("Error processing order", extra={"order_id": order_id, "error": str(error)})
```

Structured logging (JSON format) is essential for:
- Automated alerting
- Log aggregation and search
- Correlation across services
- Preventing log injection

### Missing Error Context

Check that error logging includes sufficient context:
```
grep -rn "logger\.error\|log\.error\|console\.error"
```

Good error logs include:
- What operation was being performed
- Who initiated it (user ID, not PII)
- Relevant entity IDs
- Error type and message
- Timestamp (usually automatic)

### Console.log in Production Code

```
grep -rn "console\.log\|console\.debug\|console\.info" --include="*.ts" --include="*.js"
```

Flag `console.log` statements in non-test, non-script source files. These bypass structured logging, may leak sensitive data, and clutter output.

## Remediation Summary

| Issue | Fix |
|-------|-----|
| Sensitive data in logs | Sanitise or exclude sensitive fields before logging |
| Missing audit logging | Add logging to auth, authz, and admin actions |
| Swallowed exceptions | Always log caught exceptions with context |
| Log injection | Use structured logging (JSON) with parameterised messages |
| Console.log in production | Replace with structured logger |
| Missing error context | Include operation, user ID, entity IDs in error logs |

## False Positive Guidance

- `console.log` in CLI tools, scripts, and test files is expected
- Logging `req.body` after sanitisation (removing sensitive fields) is acceptable
- Test files that verify logging behaviour may contain log statements with sensitive test data
- Debug-level logging with sensitive context that is disabled in production may be acceptable
- `password` in log messages that refer to "password reset requested" (not the actual password) is fine
