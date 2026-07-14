# A10:2025 — Mishandling of Exceptional Conditions

This is a NEW category in the OWASP Top 10 2025, replacing Server-Side Request Forgery (SSRF, which was consolidated into A01). It focuses on improper handling of errors, exceptions, and unusual states that can lead to security vulnerabilities — crashes, information disclosure, denial of service, or bypassed security checks.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-248 | Uncaught Exception |
| CWE-252 | Unchecked Return Value |
| CWE-280 | Improper Handling of Insufficient Permissions or Privileges |
| CWE-391 | Unchecked Error Condition |
| CWE-392 | Missing Report of Error Condition |
| CWE-394 | Unexpected Status Code or Return Value |
| CWE-395 | Use of NullPointerException Catch to Detect NULL Pointer Dereference |
| CWE-397 | Declaration of Throws for Generic Exception |
| CWE-754 | Improper Check for Unusual or Exceptional Conditions |
| CWE-755 | Improper Handling of Exceptional Conditions |

## Detection Patterns

### Empty Catch Blocks

Grep patterns:
```
catch\s*\([^)]*\)\s*\{\s*\}
catch\s*\{[^}]*\}  # with only whitespace/comments
except\s*:\s*pass|except\s+\w+\s*:\s*pass
rescue\s*;\s*end|rescue\s*\n\s*end
```

**JavaScript/TypeScript:**

Vulnerable:
```javascript
try { await processPayment(order); } catch (e) {}
try { await processPayment(order); } catch (e) { /* TODO */ }
```
Secure:
```javascript
try {
  await processPayment(order);
} catch (e) {
  logger.error('Payment processing failed', { orderId: order.id, error: e.message });
  throw new PaymentError('Payment could not be processed');
}
```

**Python:**

Vulnerable:
```python
try:
    process_transaction(data)
except:
    pass
except Exception:
    pass
```
Secure:
```python
try:
    process_transaction(data)
except TransactionError as e:
    logger.error("Transaction failed", extra={"error": str(e), "data_id": data.id})
    raise
```

### Overly Broad Exception Catches

Grep patterns:
```
catch\s*\(\s*(Exception|Error|Throwable|\.\.\.|e)\s*\)
except\s+(Exception|BaseException)\s*(?:as)?
rescue\s*=>|rescue\s+StandardError|rescue\s+Exception
```

Vulnerable:
```java
try {
    authenticateUser(credentials);
} catch (Exception e) {
    // Catches AuthenticationException, NullPointerException, and everything else identically
    return ResponseEntity.status(401).build();
}
```
Secure:
```java
try {
    authenticateUser(credentials);
} catch (AuthenticationException e) {
    logger.warn("Auth failed", e);
    return ResponseEntity.status(401).build();
} catch (Exception e) {
    logger.error("Unexpected error during auth", e);
    return ResponseEntity.status(500).build();
}
```

### Unhandled Promise Rejections

Grep patterns:
```
async\s+function(?!.*try)|async\s*\((?!.*try)
\.then\((?!.*\.catch)
new Promise\((?!.*reject|.*catch)
```

Vulnerable:
```javascript
app.get('/data', async (req, res) => {
  const data = await fetchExternalApi(req.query.id); // No try/catch — crashes on rejection
  res.json(data);
});
```
Secure:
```javascript
app.get('/data', async (req, res, next) => {
  try {
    const data = await fetchExternalApi(req.query.id);
    res.json(data);
  } catch (e) {
    next(e); // Pass to error handler
  }
});
```

Also check for a global unhandled rejection handler:
```
grep -rn "unhandledRejection\|uncaughtException"
```

### Go Error Handling

Grep patterns:
```
, _\s*:?=
panic\(
```

An `err` assigned but never checked (second example below) spans two lines, so a plain line-based grep cannot catch it; use a multiline-capable search:
```
rg --multiline --pcre2 ', err\s*:?=.*\n(?!\s*if\s)'
```

**Ignored errors:**

Vulnerable:
```go
result, _ := db.Query("SELECT * FROM users")  // Error silently ignored
data, err := json.Marshal(input)
// err not checked, data used anyway
```
Secure:
```go
result, err := db.Query("SELECT * FROM users")
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}
```

**Panic in library code:**

Vulnerable:
```go
func ParseConfig(data []byte) Config {
    var config Config
    if err := json.Unmarshal(data, &config); err != nil {
        panic(err) // Libraries should not panic — crashes the calling application
    }
    return config
}
```
Secure:
```go
func ParseConfig(data []byte) (Config, error) {
    var config Config
    if err := json.Unmarshal(data, &config); err != nil {
        return Config{}, fmt.Errorf("parsing config: %w", err)
    }
    return config, nil
}
```

### Error Responses Leaking Internals

Grep patterns:
```
(?i)stack.*trace|stackTrace|\.stack\b|traceback
(?i)res\.(send|json)\(.*err\)|res\.(send|json)\(.*error\.(message|stack)
(?i)detail\s*=\s*True|include_stacktrace|PROPAGATE_EXCEPTIONS
```

Vulnerable:
```javascript
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,           // Leaks internal file paths
    query: err.sql,             // Leaks database schema
  });
});
```
Secure:
```javascript
app.use((err, req, res, next) => {
  const errorId = crypto.randomUUID();
  logger.error('Request error', { errorId, error: err });
  res.status(500).json({ error: 'Internal server error', errorId });
});
```

### Null/Undefined Checks on External Data

Check that responses from external APIs, database queries, and file reads are validated:

```
grep -rn "await fetch\|await axios\|await http\.\|\.json()"
```

Look for missing null checks on:
- API response bodies
- Database query results (especially `.findOne()`, `.get()`)
- File read results
- Environment variables used at runtime

### Security Check Bypass via Exception

Look for security checks where an exception skips the check entirely:

Vulnerable:
```python
try:
    user = get_user(token)
    if not user.is_admin:
        raise Forbidden()
except:
    pass  # Exception during auth check allows unauthenticated access!
```

## Remediation Summary

| Issue | Fix |
|-------|-----|
| Empty catch blocks | Log error and handle appropriately (rethrow, return error response, fallback) |
| Broad exception catches | Catch specific exceptions, handle each appropriately |
| Unhandled promises | Wrap async handlers in try/catch, add global rejection handler |
| Ignored Go errors | Always check and propagate errors |
| Panic in libraries | Return errors instead of panicking |
| Stack traces in responses | Log internally, return generic message with error ID |
| Missing null checks | Validate all external data before use |

## False Positive Guidance

- Empty catch blocks in cleanup/teardown code (e.g., closing resources that may already be closed) can be acceptable if intentional
- `panic()` in Go `main()` or `init()` functions is acceptable for unrecoverable startup errors
- Broad catches that re-throw after logging are a valid pattern
- Test code may intentionally trigger and catch exceptions
- `catch (e) { throw e }` (catch-and-rethrow for finally blocks) is fine
- Some frameworks (Express 5, Koa, FastAPI) handle async errors automatically — verify before flagging
