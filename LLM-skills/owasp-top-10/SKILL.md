---
name: owasp-top-10
description: >-
  Analyze code for OWASP Top 10 2025 security vulnerabilities.
  This skill should be used when the user asks to "check for security vulnerabilities",
  "run a security audit", "OWASP scan", "find security issues", "review for security",
  "check OWASP", or mentions specific OWASP categories like "A01" through "A10".
allowed-tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *), Bash(git status *)
metadata:
  argument-hint: "[file-or-directory] [A01-A10] [--changed]"
---

# OWASP Top 10 2025 Security Analysis

Perform a structured security analysis of code against the OWASP Top 10 2025 vulnerability categories. Produce a severity-rated report with CWE references and actionable remediation guidance.

## 1. Parse Arguments and Determine Scope

Interpret `$ARGUMENTS` to determine what to scan:

- **File path** (e.g., `src/auth.ts`) → scan that file
- **Directory path** (e.g., `src/`) → scan all code files in that directory recursively
- **Category code** (e.g., `A01`, `A05`) → filter analysis to those categories only
- **`--changed`** → scan only git-changed files (staged + unstaged)
- **No arguments** → default to scanning git-changed files
- Arguments combine: `/owasp src/api/ A01 A07` scans `src/api/` for only A01 and A07

When scanning directories, exclude: `node_modules/`, `vendor/`, `dist/`, `build/`, `.git/`, `__pycache__/`, `.venv/`, `target/`, `*.min.js`, `*.lock`, `*.map`.

## 2. Discovery Phase

1. Enumerate files in scope using Glob (for paths) or `git diff --name-only HEAD` and `git diff --cached --name-only` (for changed files mode)
2. Identify the tech stack from file extensions and package manifests:
   - `package.json` / `yarn.lock` → Node.js / JavaScript / TypeScript
   - `requirements.txt` / `pyproject.toml` / `Pipfile` → Python
   - `go.mod` → Go
   - `pom.xml` / `build.gradle` → Java
   - `Gemfile` → Ruby
   - `Cargo.toml` → Rust
   - `composer.json` → PHP
3. Note detected frameworks (Express, Django, Flask, FastAPI, Spring Boot, Gin, Rails, Laravel, etc.) as these inform which patterns to prioritize

## 3. Analysis Workflow

Work through each applicable OWASP category systematically. Use Grep to scan for suspicious patterns, then Read to examine context around matches. Load the detailed reference file for any category where findings are detected or analysis requires deeper patterns.

Copy and update this progress tracker:

```
Security Analysis Progress:
- [ ] Scope determined and files enumerated
- [ ] Tech stack identified
- [ ] A01: Broken Access Control
- [ ] A02: Security Misconfiguration
- [ ] A03: Software Supply Chain Failures
- [ ] A04: Cryptographic Failures
- [ ] A05: Injection
- [ ] A06: Insecure Design
- [ ] A07: Authentication Failures
- [ ] A08: Software or Data Integrity Failures
- [ ] A09: Security Logging & Alerting Failures
- [ ] A10: Mishandling of Exceptional Conditions
- [ ] Report generated
```

## 4. Quick-Reference Detection Patterns

Use these patterns as a fast first pass. For comprehensive analysis, load the linked reference file.

### A01:2025 — Broken Access Control
Grep for: route/endpoint definitions missing auth middleware, direct database ID usage in request parameters without ownership validation, `Access-Control-Allow-Origin: *`, missing RBAC/ABAC checks, path traversal patterns (`../`, user-controlled file paths).
See [A01-broken-access-control.md](references/A01-broken-access-control.md) for framework-specific patterns.

### A02:2025 — Security Misconfiguration
Grep for: `DEBUG = True` or `debug: true` in production configs, default credentials (`admin/admin`, `password`), verbose error responses exposing internals, missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options), overly permissive CORS, unnecessary HTTP methods enabled.
See [A02-security-misconfiguration.md](references/A02-security-misconfiguration.md) for config-specific patterns.

### A03:2025 — Software Supply Chain Failures
Check: lockfile presence and integrity hashes, unpinned dependency versions (`*`, `latest`), `pre/postinstall` scripts fetching external URLs, CI/CD actions using `@main` instead of SHA pins, deprecated or known-vulnerable packages, unsigned build artifacts.
See [A03-supply-chain-failures.md](references/A03-supply-chain-failures.md) for manifest analysis patterns.

### A04:2025 — Cryptographic Failures
Grep for: weak algorithms (`MD5`, `SHA1` for security purposes, `DES`, `RC4`, `ECB`), hardcoded secrets/keys/passwords, `Math.random()` or `random.random()` for security-sensitive operations, missing TLS enforcement, key lengths < 2048 (RSA) or < 256 (ECC), plaintext storage of sensitive data.
See [A04-cryptographic-failures.md](references/A04-cryptographic-failures.md) for algorithm-specific patterns.

### A05:2025 — Injection
Grep for: string concatenation/interpolation in SQL queries, `eval()` / `exec()` / `Function()` with dynamic input, `child_process.exec` / `subprocess.run(shell=True)` / `os.system()` with user input, `innerHTML` / `dangerouslySetInnerHTML` / `v-html`, ORM raw query methods, LDAP filter construction with user input, template rendering with unsanitized variables.
See [A05-injection.md](references/A05-injection.md) for language-specific injection vectors.

### A06:2025 — Insecure Design
Look for: missing rate limiting on authentication/password reset/payment endpoints, absence of input validation schemas, no separation between user and admin code paths, missing business logic abuse protections (e.g., negative quantities, race conditions on balances), lack of CAPTCHA on public-facing forms.
See [A06-insecure-design.md](references/A06-insecure-design.md) for design-level review guidance.

### A07:2025 — Authentication Failures
Grep for: weak password policies (short min length, no complexity), missing MFA support, session tokens in URLs or localStorage, no account lockout or rate limiting on login, plaintext password storage or weak hashing (`MD5`, `SHA1`, unsalted), JWT with no expiration or `alg: none`, credential exposure in logs.
See [A07-authentication-failures.md](references/A07-authentication-failures.md) for auth-specific patterns.

### A08:2025 — Software or Data Integrity Failures
Check for: deserialization of untrusted data (`pickle.loads`, `yaml.load` without SafeLoader, Java `ObjectInputStream`, PHP `unserialize`), missing Subresource Integrity (SRI) on CDN scripts, auto-update mechanisms without signature verification, CI/CD pipelines with injectable environment variables, unsigned deployments.
See [A08-integrity-failures.md](references/A08-integrity-failures.md) for deserialization and CI/CD patterns.

### A09:2025 — Security Logging & Alerting Failures
Grep for: sensitive data in log statements (passwords, tokens, credit cards, PII), missing audit logging on authentication events, `catch` blocks that swallow exceptions silently (empty catch, catch-and-ignore), no structured logging format, log injection vulnerabilities (unsanitized user input in log messages), missing logging on access control failures.
See [A09-logging-alerting-failures.md](references/A09-logging-alerting-failures.md) for logging audit patterns.

### A10:2025 — Mishandling of Exceptional Conditions
Grep for: empty `catch`/`except`/`rescue` blocks, overly broad exception catches (`catch (Exception e)`, `except Exception`, `catch (...)`) that mask specific errors, missing null/undefined checks on external API responses, unhandled promise rejections (`async` without `try/catch`, missing `.catch()`), `panic()` in Go library code (should return errors), error responses leaking stack traces or internal paths.
See [A10-exceptional-conditions.md](references/A10-exceptional-conditions.md) for error handling patterns.

## 5. Report Format

Present findings using this structure:

```markdown
# OWASP Top 10 2025 — Security Analysis Report

## Summary
- **Scope**: [files/directories scanned, count of files]
- **Tech stack**: [detected languages, frameworks]
- **Findings**: X critical, Y high, Z medium, W low

---

## Critical Findings

### [A0X] Finding title
- **Severity**: Critical
- **Category**: A0X:2025 — Category Name
- **CWE**: CWE-XXX (Name)
- **Location**: `path/to/file.ext:LINE`
- **Description**: What the vulnerability is and why it matters
- **Evidence**:
  ```lang
  // relevant code snippet, 3-5 lines
  ```
- **Remediation**: Specific fix with code example

---

## High Findings
[Same structure as above]

## Medium Findings
[Same structure as above]

## Low Findings
[Same structure as above]

---

## Recommendations
1. [Prioritized action items]
2. [Additional hardening suggestions]
3. [References to OWASP documentation for further reading]
```

If no findings are detected for a severity level, omit that section. If no vulnerabilities are found at all, state that the scanned code passed the analysis and suggest areas for manual review.

## 6. Severity Classification

- **Critical**: Directly exploitable with high impact — RCE, SQL injection, hardcoded admin credentials, deserialization leading to code execution
- **High**: Exploitable under realistic conditions with significant impact — broken access control bypasses, weak cryptography on sensitive data, authentication bypasses
- **Medium**: Requires specific circumstances or has moderate impact — missing security headers, verbose error messages, overly permissive CORS
- **Low**: Defense-in-depth issues with minimal direct exploitability — missing SRI attributes, debug logging in non-sensitive areas, informational header leakage

When severity is ambiguous, consider: exploitability (how easy), impact (what is at risk), and scope (how much is affected). Err on the side of higher severity for findings involving authentication, authorization, or sensitive data.
