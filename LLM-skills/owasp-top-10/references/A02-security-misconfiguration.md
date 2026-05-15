# A02:2025 — Security Misconfiguration

Security misconfiguration is the most common issue in cloud and web applications. It includes missing security hardening, improperly configured permissions, unnecessary features enabled, default accounts/passwords, and overly informative error messages.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-2 | Environmental Security Flaws |
| CWE-11 | ASP.NET Misconfiguration |
| CWE-16 | Configuration |
| CWE-209 | Information Exposure Through an Error Message |
| CWE-215 | Insertion of Sensitive Information Into Debugging Code |
| CWE-548 | Exposure of Information Through Directory Listing |
| CWE-611 | Improper Restriction of XML External Entity Reference (XXE) |

## Detection Patterns

### Debug Mode in Production

Grep patterns:
```
(?i)DEBUG\s*=\s*True|debug\s*:\s*true|debug\s*=\s*true
(?i)NODE_ENV.*development|FLASK_ENV.*development|RAILS_ENV.*development
(?i)app\.debug\s*=\s*True|\.setDebug\(true\)
```

Flag when found in production configuration files, not development/test configs.

### Default Credentials

Grep patterns:
```
(?i)(password|passwd|pwd)\s*[=:]\s*["'](admin|password|123456|root|default|changeme|test)["']
(?i)(username|user)\s*[=:]\s*["'](admin|root|administrator|sa)["']
```

### Missing Security Headers

Check HTTP response configuration for:

```
(?i)X-Frame-Options|Content-Security-Policy|X-Content-Type-Options|Strict-Transport-Security
(?i)X-XSS-Protection|Referrer-Policy|Permissions-Policy
```

**Express/Node.js** — check for helmet middleware:
```
grep -n "helmet\|X-Frame-Options\|Content-Security-Policy"
```

Vulnerable:
```javascript
app.listen(3000); // No security headers
```
Secure:
```javascript
const helmet = require('helmet');
app.use(helmet());
```

**Django** — check settings:
```
grep -n "SECURE_HSTS\|CSP_\|X_FRAME_OPTIONS\|SECURE_CONTENT_TYPE_NOSNIFF"
```

### Verbose Error Responses

Grep patterns:
```
(?i)stack.*trace|stackTrace|printStackTrace|traceback
(?i)res\.send\(err\)|res\.json\(.*error.*message|res\.status\(500\)\.send\(e
(?i)detail\s*=\s*True|include_stacktrace
```

Vulnerable:
```javascript
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, stack: err.stack });
});
```
Secure:
```javascript
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(500).json({ error: 'Internal server error' });
});
```

### XML External Entity (XXE)

Grep patterns:
```
(?i)XMLParser|SAXParser|DocumentBuilder|etree\.parse|xml\.parse|lxml
(?i)FEATURE_EXTERNAL_ENTITIES|resolve_entities|load_external_dtd
```

Vulnerable:
```python
from lxml import etree
doc = etree.parse(user_input)
```
Secure:
```python
from defusedxml import ElementTree
doc = ElementTree.parse(user_input)
```

### Unnecessary Features

Look for:
- Directory listing enabled in web server configs
- Sample/example applications deployed
- Admin consoles accessible without auth
- Unnecessary HTTP methods (TRACE, OPTIONS on all routes)
- GraphQL introspection enabled in production

### Cloud / Infrastructure Misconfigurations

Grep patterns in IaC files (Terraform, CloudFormation, K8s manifests):
```
(?i)public.*true|publicly_accessible.*true|PubliclyAccessible.*true
(?i)0\.0\.0\.0/0|::/0
(?i)privileged.*true|runAsRoot.*true|allowPrivilegeEscalation.*true
```

## Remediation Checklist

- [ ] Disable debug mode in production
- [ ] Remove default credentials
- [ ] Implement security headers (use helmet/equivalent)
- [ ] Configure error handling to not expose internals
- [ ] Disable XXE processing or use defused parsers
- [ ] Remove unnecessary features and sample apps
- [ ] Restrict cloud resource access to least-privilege
- [ ] Disable directory listing

## False Positive Guidance

- Debug mode in `development.env` or `docker-compose.dev.yml` is expected
- Default credentials in test fixtures, seeds, or example configs (not deployed) are acceptable
- Verbose errors in development error handlers (behind NODE_ENV check) are fine
- `0.0.0.0` as a listen address (not a CIDR allowlist) is common in containers
- GraphQL introspection in development is standard practice
