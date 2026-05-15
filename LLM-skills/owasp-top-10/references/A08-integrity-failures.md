# A08:2025 — Software or Data Integrity Failures

This category focuses on code and infrastructure that does not protect against integrity violations — assumptions about software updates, critical data, and CI/CD pipelines without verifying integrity. Insecure deserialization is included here.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-345 | Insufficient Verification of Data Authenticity |
| CWE-353 | Missing Support for Integrity Check |
| CWE-426 | Untrusted Search Path |
| CWE-494 | Download of Code Without Integrity Check |
| CWE-502 | Deserialization of Untrusted Data |
| CWE-565 | Reliance on Cookies without Validation or Integrity Checking |
| CWE-784 | Reliance on Cookies without Validation in Security Decision |
| CWE-830 | Inclusion of Web Functionality from Untrusted Source |

## Detection Patterns

### Insecure Deserialization

**Python:**
```
pickle\.loads\(|pickle\.load\(|shelve\.open\(|marshal\.loads\(
yaml\.load\((?!.*Loader\s*=\s*yaml\.SafeLoader)|yaml\.unsafe_load\(
```

Vulnerable:
```python
import pickle
data = pickle.loads(request.body)  # Arbitrary code execution

import yaml
config = yaml.load(user_input)  # Code execution via YAML tags
```
Secure:
```python
import json
data = json.loads(request.body)  # Safe — no code execution

import yaml
config = yaml.safe_load(user_input)  # Safe — only basic types
```

**Java:**
```
ObjectInputStream|readObject\(|XMLDecoder|XStream|Kryo
JsonParser.*enableDefaultTyping|ObjectMapper.*enableDefaultTyping
```

Vulnerable:
```java
ObjectInputStream ois = new ObjectInputStream(userInputStream);
Object obj = ois.readObject();  // Arbitrary code execution
```
Secure:
```java
// Use allowlisting with ObjectInputFilter (Java 9+)
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter("com.myapp.**;!*");
ois.setObjectInputFilter(filter);
```

**PHP:**
```
unserialize\(.*\$_(GET|POST|REQUEST|COOKIE)
```

**JavaScript/Node.js:**
```
node-serialize|serialize-javascript.*eval|cryo\.parse
```

Note: `JSON.parse()` is safe — it cannot execute code.

### CI/CD Pipeline Integrity

**Unsigned or unverified deployments:**
Check deployment scripts for integrity verification:
```
grep -rn "curl.*\| sh\|curl.*\| bash\|wget.*\| sh"
grep -rn "pip install.*http\|npm install.*http\|gem install.*--source.*http"
```

Flag: downloading and executing scripts from URLs without checksum verification.

**CI/CD injection via pull request:**
```
grep -rn "pull_request_target" .github/workflows/
```
`pull_request_target` runs with write permissions and access to secrets — check that it doesn't checkout PR code and run it.

**Mutable deployment artifacts:**
Check that build artifacts are tagged/versioned, not overwritten:
```
grep -rn ":latest\b" --include="*.yml" --include="*.yaml" --include="Dockerfile"
```
Flag Docker images using `:latest` tag in production deployments.

### Missing Subresource Integrity (SRI)

```
grep -rn "<script.*src=.*https\?://\|<link.*href=.*https\?://" --include="*.html" --include="*.ejs" --include="*.hbs"
```

Check that external resources have `integrity` and `crossorigin` attributes.

### Cookie Integrity

```
grep -rn "cookie\|Cookie" --include="*.js" --include="*.ts" --include="*.py" --include="*.java"
```

Check that security-sensitive cookies:
- Are signed (HMAC or equivalent)
- Have `httpOnly`, `secure`, `sameSite` attributes
- Are not used for authorization decisions without server-side validation

### Auto-Update Without Verification

Look for update mechanisms that don't verify signatures:
```
grep -rn "auto.update\|autoUpdate\|self.update\|checkForUpdates"
```

Ensure downloaded updates are verified against a signing key before installation.

## Remediation Summary

| Issue | Fix |
|-------|-----|
| Pickle deserialization | Use JSON or MessagePack; never unpickle untrusted data |
| YAML unsafe load | Use `yaml.safe_load()` or `yaml.load(data, Loader=SafeLoader)` |
| Java ObjectInputStream | Use allowlist filtering or switch to JSON |
| Curl pipe to shell | Download, verify checksum, then execute |
| Docker :latest | Use specific version tags or SHA digests |
| Missing SRI | Add integrity hash to external script/link tags |
| Unsigned cookies | Sign cookies with HMAC |

## False Positive Guidance

- `pickle` in ML model loading from trusted local files is common — flag but note the trust boundary
- `yaml.load` with `Loader=SafeLoader` or `yaml.safe_load` is secure
- `:latest` in development docker-compose files is normal
- `curl | sh` in documented local development setup scripts is lower risk than in CI/CD
- `ObjectInputStream` reading from trusted internal sources (not user input) is lower risk
- `JSON.parse()`, `json.loads()`, `json.Unmarshal()` are safe deserializers
