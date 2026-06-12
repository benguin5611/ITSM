---
name: owasp-top-10
description: >-
  Analyze code for OWASP security vulnerabilities across three lists:
  Web Top 10 2025 (A01–A10), API Security Top 10 2023 (API1–API10), and
  LLM AI Security Top 10 2025 (LLM01–LLM10).
  This skill should be used when the user asks to "check for security vulnerabilities",
  "run a security audit", "OWASP scan", "find security issues", "review for security",
  "check OWASP", or mentions specific category codes like "A01", "API3", or "LLM06".
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git log:*), Bash(git status:*)
metadata:
  argument-hint: "[file-or-directory] [A01-A10|API1-API10|LLM01-LLM10] [--changed] [--web|--api|--llm]"
---

# OWASP Security Analysis

Perform a structured security analysis against three OWASP Top 10 lists:
- **Web 2025** (A01–A10): general web application vulnerabilities
- **API 2023** (API1–API10): REST/GraphQL/gRPC API-specific risks
- **LLM 2025** (LLM01–LLM10): AI/LLM application vulnerabilities

Produce a severity-rated report with CWE references and actionable remediation guidance.

## Which lists apply?

Apply each list based on what the codebase contains — not by default for everything:

| List | Apply when | Skip when |
|------|-----------|-----------|
| **Web Top 10 2025** (A01–A10) | Always — covers all server-side and frontend code | Never skip |
| **API Top 10 2023** (API1–API10) | Any REST/GraphQL/gRPC routes exist, or an OpenAPI/Swagger spec is present | Pure CLI tool, batch job, or library with no HTTP surface |
| **LLM Top 10 2025** (LLM01–LLM10) | LLM SDK (`openai`, `anthropic`, `langchain`, etc.) found in deps, OR vector store client present, OR `--llm` flag passed | No LLM integration detected |

**Flags override auto-detection**: `--web`, `--api`, `--llm` restrict the run to only that list. Explicit category codes (e.g. `API3`, `LLM06`) also restrict to only those categories regardless of auto-detection.

The Web and API lists overlap intentionally — A01 (broken access control) and API1 (BOLA) address the same root cause from different angles. Flag both when both patterns are present in the same file.

## 1. Parse Arguments and Determine Scope

Interpret `$ARGUMENTS` to determine what to scan:

- **File path** (e.g., `src/auth.ts`) → scan that file
- **Directory path** (e.g., `src/`) → scan all code files in that directory recursively
- **Web category code** (e.g., `A01`, `A05`) → filter to those Web categories only
- **API category code** (e.g., `API1`, `API5`) → filter to those API categories only
- **LLM category code** (e.g., `LLM01`, `LLM06`) → filter to those LLM categories only
- **`--changed`** → scan only git-changed files (staged + unstaged)
- **`--web`** → restrict analysis to Web Top 10 categories only
- **`--api`** → restrict analysis to API Top 10 categories only
- **`--llm`** → restrict analysis to LLM Top 10 categories only
- **No arguments** → default to scanning git-changed files across all applicable lists
- Arguments combine: `/owasp src/api/ A01 API1` scans `src/api/` for A01 and API1 only

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
3. Note detected frameworks (Express, Django, Flask, FastAPI, Spring Boot, Gin, Rails, Laravel, etc.) as these inform which patterns to prioritise
4. Detect LLM integrations to determine if LLM Top 10 is applicable:
   - `openai`, `anthropic`, `@anthropic-ai/sdk` in dependencies
   - `langchain`, `llamaindex`, `llama-index`, `semantic-kernel` in dependencies
   - Imports of `ChatOpenAI`, `Anthropic`, `openai.chat.completions`, etc.
   - Presence of vector store clients (`pinecone`, `weaviate`, `chroma`, `qdrant`)
   - If no LLM integrations detected and `--llm` not specified, skip LLM Top 10
5. Detect API patterns to determine API Top 10 applicability:
   - REST route handlers, OpenAPI/Swagger specs, gRPC proto files, GraphQL schemas
   - If the codebase has API endpoints (almost always true), include API Top 10

## 3. Analysis Workflow

Work through each applicable OWASP category systematically. Use Grep to scan for suspicious patterns, then Read to examine context around matches. Load the relevant reference file for any category where findings are detected or analysis requires deeper patterns.

Copy and update this progress tracker:

```
Security Analysis Progress:
- [ ] Scope determined and files enumerated
- [ ] Tech stack identified
- [ ] LLM integrations detected? (yes/no)

=== Web Top 10 2025 ===
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

=== API Security Top 10 2023 ===
- [ ] API1: Broken Object Level Authorization (BOLA)
- [ ] API2: Broken Authentication
- [ ] API3: Broken Object Property Level Authorization
- [ ] API4: Unrestricted Resource Consumption
- [ ] API5: Broken Function Level Authorization (BFLA)
- [ ] API6: Unrestricted Access to Sensitive Business Flows
- [ ] API7: Server Side Request Forgery
- [ ] API8: Security Misconfiguration
- [ ] API9: Improper Inventory Management
- [ ] API10: Unsafe Consumption of APIs

=== LLM AI Security Top 10 2025 (if applicable) ===
- [ ] LLM01: Prompt Injection
- [ ] LLM02: Sensitive Information Disclosure
- [ ] LLM03: Supply Chain
- [ ] LLM04: Data and Model Poisoning
- [ ] LLM05: Improper Output Handling
- [ ] LLM06: Excessive Agency
- [ ] LLM07: System Prompt Leakage
- [ ] LLM08: Vector and Embedding Weaknesses
- [ ] LLM09: Misinformation
- [ ] LLM10: Unbounded Consumption

- [ ] Report generated
```

## 4. Quick-Reference Detection Patterns

Use these patterns as a fast first pass. For comprehensive analysis, load the linked reference files.

---

### Web Top 10 2025

#### A01:2025 — Broken Access Control
Grep for: route/endpoint definitions missing auth middleware, direct database ID usage in request parameters without ownership validation, `Access-Control-Allow-Origin: *`, missing RBAC/ABAC checks, path traversal patterns (`../`, user-controlled file paths).
See [A01-broken-access-control.md](references/A01-broken-access-control.md) for framework-specific patterns.

#### A02:2025 — Security Misconfiguration
Grep for: `DEBUG = True` or `debug: true` in production configs, default credentials (`admin/admin`, `password`), verbose error responses exposing internals, missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options), overly permissive CORS, unnecessary HTTP methods enabled.
See [A02-security-misconfiguration.md](references/A02-security-misconfiguration.md) for config-specific patterns.

#### A03:2025 — Software Supply Chain Failures
Check: lockfile presence and integrity hashes, unpinned dependency versions (`*`, `latest`), `pre/postinstall` scripts fetching external URLs, CI/CD actions using `@main` instead of SHA pins, deprecated or known-vulnerable packages, unsigned build artifacts.
See [A03-supply-chain-failures.md](references/A03-supply-chain-failures.md) for manifest analysis patterns.

#### A04:2025 — Cryptographic Failures
Grep for: weak algorithms (`MD5`, `SHA1` for security purposes, `DES`, `RC4`, `ECB`), hardcoded secrets/keys/passwords, `Math.random()` or `random.random()` for security-sensitive operations, missing TLS enforcement, key lengths < 2048 (RSA) or < 256 (ECC), plaintext storage of sensitive data.
See [A04-cryptographic-failures.md](references/A04-cryptographic-failures.md) for algorithm-specific patterns.

#### A05:2025 — Injection
Grep for: string concatenation/interpolation in SQL queries, `eval()` / `exec()` / `Function()` with dynamic input, `child_process.exec` / `subprocess.run(shell=True)` / `os.system()` with user input, `innerHTML` / `dangerouslySetInnerHTML` / `v-html`, ORM raw query methods, LDAP filter construction with user input, template rendering with unsanitised variables.
See [A05-injection.md](references/A05-injection.md) for language-specific injection vectors.

#### A06:2025 — Insecure Design
Look for: missing rate limiting on authentication/password reset/payment endpoints, absence of input validation schemas, no separation between user and admin code paths, missing business logic abuse protections (e.g. negative quantities, race conditions on balances), lack of CAPTCHA on public-facing forms.
See [A06-insecure-design.md](references/A06-insecure-design.md) for design-level review guidance.

#### A07:2025 — Authentication Failures
Grep for: weak password policies (short min length, no complexity), missing MFA support, session tokens in URLs or localStorage, no account lockout or rate limiting on login, plaintext password storage or weak hashing (`MD5`, `SHA1`, unsalted), JWT with no expiration or `alg: none`, credential exposure in logs.
See [A07-authentication-failures.md](references/A07-authentication-failures.md) for auth-specific patterns.

#### A08:2025 — Software or Data Integrity Failures
Check for: deserialization of untrusted data (`pickle.loads`, `yaml.load` without SafeLoader, Java `ObjectInputStream`, PHP `unserialize`), missing Subresource Integrity (SRI) on CDN scripts, auto-update mechanisms without signature verification, CI/CD pipelines with injectable environment variables, unsigned deployments.
See [A08-integrity-failures.md](references/A08-integrity-failures.md) for deserialization and CI/CD patterns.

#### A09:2025 — Security Logging & Alerting Failures
Grep for: sensitive data in log statements (passwords, tokens, credit cards, PII), missing audit logging on authentication events, `catch` blocks that swallow exceptions silently (empty catch, catch-and-ignore), no structured logging format, log injection vulnerabilities (unsanitised user input in log messages), missing logging on access control failures.
See [A09-logging-alerting-failures.md](references/A09-logging-alerting-failures.md) for logging audit patterns.

#### A10:2025 — Mishandling of Exceptional Conditions
Grep for: empty `catch`/`except`/`rescue` blocks, overly broad exception catches (`catch (Exception e)`, `except Exception`, `catch (...)`) that mask specific errors, missing null/undefined checks on external API responses, unhandled promise rejections (`async` without `try/catch`, missing `.catch()`), `panic()` in Go library code (should return errors), error responses leaking stack traces or internal paths.
See [A10-exceptional-conditions.md](references/A10-exceptional-conditions.md) for error handling patterns.

---

### API Security Top 10 2023

#### API1:2023 — Broken Object Level Authorization (BOLA / IDOR)
Grep for: route handlers that accept an object ID from the URL/body/query and query the database directly without verifying the requesting user owns or has permission to that record. Look for patterns like `getById(req.params.id)` or `WHERE id = $userInput` with no subsequent ownership check. Check GraphQL resolvers — mutations that accept an `ID` argument and operate on the record without re-validating ownership are vulnerable.
CWEs: CWE-285, CWE-639.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API2:2023 — Broken Authentication
Grep for: missing rate limiting on `/login`, `/forgot-password`, `/reset-password` endpoints, credentials or tokens appearing in URLs (`?token=`, `?key=`), `alg: "none"` in JWT handling, no JWT expiry check, weak or predictable token generation, microservice-to-microservice calls without authentication, GraphQL batching enabling brute force by sending multiple login mutations in one request.
CWEs: CWE-204, CWE-307.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API3:2023 — Broken Object Property Level Authorization
Look for: serialisers or response mappers that call `.toJSON()` / `.serialize()` / ORM `.toObject()` without explicitly whitelisting returned fields (returning all columns including sensitive ones). Also look for mass assignment patterns — controllers that pass `req.body` directly into an ORM `update()` or `create()` without a permitted-fields allowlist. Check for fields like `role`, `isAdmin`, `balance`, `blocked` that a user should not be able to set.
CWEs: CWE-213, CWE-915.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API4:2023 — Unrestricted Resource Consumption
Grep for: pagination parameters (`limit`, `page_size`, `first`) with no server-side maximum cap, GraphQL queries without depth/complexity limits, no rate limiting middleware on costly endpoints (file upload, image processing, email/SMS triggers), no execution timeouts on long-running operations, third-party API calls (SMS, email, payment) triggered without per-user rate limits or spending caps.
CWEs: CWE-770, CWE-400, CWE-799.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API5:2023 — Broken Function Level Authorization (BFLA)
Grep for: admin/management endpoints (`/admin`, `/internal`, `/management`, `_all`, `export`) that do not verify the caller's role/group before executing. Check HTTP method handling — can a `GET` endpoint be called as `DELETE` with the same handler? Look for privilege-escalation vectors like `POST /api/invites/new` with a `role` field that skips RBAC checks. Verify all controllers requiring elevated access call a shared authorisation guard.
CWEs: CWE-285.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API6:2023 — Unrestricted Access to Sensitive Business Flows
Look for: high-value or rate-sensitive business operations (purchase, booking, referral redemption, voting, ticket reservation) with no bot/automation protection — missing CAPTCHA, device fingerprinting, or non-human behaviour detection. Check for flows where automated abuse causes direct business harm (inventory depletion, financial loss, spam). Rate limiting alone is insufficient if per-account limits are not enforced.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API7:2023 — Server Side Request Forgery (SSRF)
Grep for: any endpoint that accepts a user-supplied URL and fetches it server-side — webhooks, avatar/image URL fetching, URL preview generation, custom SSO callback URLs, file imports from URL. Look for `fetch(userInput)`, `axios.get(req.body.url)`, `http.Get(url)` where `url` derives from request data with no allowlist validation. Cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`) are a critical SSRF target.
CWEs: CWE-918.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API8:2023 — Security Misconfiguration (API-specific)
Check: missing or overly permissive CORS headers on API routes, TLS not enforced between services (internal HTTP without TLS), verbose error responses that include stack traces or internal paths, unnecessary HTTP verbs enabled (e.g. TRACE), missing `Cache-Control: no-store` on responses containing sensitive data, JNDI/log4shell-style lookup expansion in logging configs, S3 bucket permissions too open.
CWEs: CWE-2, CWE-16, CWE-209, CWE-319, CWE-444, CWE-942.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API9:2023 — Improper Inventory Management
Look for: multiple API version prefixes (`/v1/`, `/v2/`, `/beta/`) with no evidence of deprecation/retirement plan, undocumented or debug endpoints (`/debug`, `/health?full=true`, `/swagger` exposed in production), staging/test API hosts accessible from the public internet, shared databases between production and non-production API deployments, no OpenAPI/Swagger spec or stale documentation.
CWEs: CWE-1059.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

#### API10:2023 — Unsafe Consumption of APIs
Grep for: data fetched from third-party APIs passed directly into downstream operations without validation — e.g. third-party address data used in a SQL query, third-party webhook payload fields used in a template render. Check for unconditional redirect following when consuming external APIs. Look for missing timeouts or connection limits on outbound API calls. Verify third-party API responses are treated with the same suspicion as user input.
CWEs: CWE-20, CWE-200, CWE-319.
See [API-top10-2023.md](references/API-top10-2023.md) for detailed patterns.

---

### LLM AI Security Top 10 2025 (scan only when LLM integrations detected)

#### LLM01:2025 — Prompt Injection
Grep for: user-controlled input concatenated directly into a system prompt string (template literals mixing system instructions and user data). Look for tool/function calling where arguments are constructed from user input without sanitisation. Check for indirect injection: LLM reads from external sources (web pages, documents, emails) that could contain adversarial instructions. Multi-agent pipelines where one agent's output becomes another's prompt are high-risk.
CWEs: CWE-77, CWE-94.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM02:2025 — Sensitive Information Disclosure
Look for: system prompts that contain API keys, credentials, or PII that could be extracted via prompt injection. Check whether the model can be made to repeat its context window. Verify that RAG retrieval pipelines apply access control before returning chunks — a user should not retrieve documents they lack permission to read. Check logs for LLM completions that may capture sensitive user data.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM03:2025 — Supply Chain
Check: model source and integrity — is the model from a trusted provider, or loaded from an untrusted registry? Are model weights pinned to a specific version/hash? Are LLM orchestration libraries (`langchain`, `llamaindex`) pinned and audited? Check fine-tuning pipelines for untrusted training data sources. Verify that third-party plugins or tool integrations are reviewed before use.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM04:2025 — Data and Model Poisoning
Look for: RAG knowledge bases or vector stores populated from untrusted or user-submitted sources without review/sanitisation. Fine-tuning pipelines that ingest unvalidated external data. Embedding pipelines that lack input validation — adversarially crafted documents could skew retrieval results. Check whether feedback loops (thumbs up/down → re-training) have safeguards against adversarial labelling.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM05:2025 — Improper Output Handling
Grep for: LLM output used directly in SQL queries, shell commands, HTML renders (XSS), JavaScript `eval()`, file system operations, or API calls without sanitisation. Look for `innerHTML = llmOutput`, `exec(llmOutput)`, `query(llmOutput)`, or passing LLM-generated code to a runtime without sandboxing. The LLM's output must be treated as untrusted input.
CWEs: CWE-79, CWE-78, CWE-89.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM06:2025 — Excessive Agency
Look for: LLM agents granted write, delete, send, or execute capabilities without a human-in-the-loop confirmation step for destructive or irreversible actions. Check tool definitions — does the agent have access to email sending, database writes, file deletion, or external API calls with side effects? Verify that the principle of least privilege is applied: high-impact actions should require explicit user confirmation.
CWEs: CWE-269, CWE-732.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM07:2025 — System Prompt Leakage
Grep for: system prompts containing secrets, API keys, internal IP addresses, proprietary business logic, or sensitive instructions. Verify the application does not expose the system prompt via debug endpoints or error messages. Test whether a user can extract the system prompt via adversarial instructions ("repeat your instructions verbatim"). Sensitive security controls should not live solely in the system prompt.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM08:2025 — Vector and Embedding Weaknesses
Look for: vector store retrieval that does not enforce the user's access level — returned chunks may contain documents from other users/tenants. Check for embedding model supply chain issues (untrusted embedding model). Verify that vector store namespace/tenant isolation is correct in multi-tenant applications. Look for adversarial document injection into shared RAG stores that could manipulate retrieval for other users.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM09:2025 — Misinformation
Look for: application logic that trusts LLM output for safety-critical decisions without a verification step (medical dosing, legal advice, financial calculations). Check whether hallucinated URLs, citations, or code are passed through to users without a disclaimer. Verify the application has fallback handling for low-confidence LLM output. Agentic systems that make real-world decisions solely on LLM reasoning are high-risk.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

#### LLM10:2025 — Unbounded Consumption
Grep for: LLM API calls with no token limits (`max_tokens` unset or extremely high), no per-user or per-session request rate limits, no cost alerting or spending caps on the AI provider account. Look for recursive or looping agent patterns with no iteration cap. Check for streaming responses with no timeout or max-size guard. Denial-of-wallet attacks are possible if a user can trigger expensive LLM calls without resource guardrails.
CWEs: CWE-770, CWE-400.
See [LLM-top10-2025.md](references/LLM-top10-2025.md) for detailed patterns.

---

## 5. Report Format

Present findings using this structure:

```markdown
# OWASP Security Analysis Report

## Summary
- **Scope**: [files/directories scanned, count of files]
- **Tech stack**: [detected languages, frameworks]
- **Lists applied**: Web Top 10 2025 / API Top 10 2023 / LLM Top 10 2025
- **Findings**: X critical, Y high, Z medium, W low

---

## Critical Findings

### [CATEGORY-CODE] Finding title
- **Severity**: Critical
- **Category**: [A0X:2025 / API1:2023 / LLM01:2025] — Category Name
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
1. [Prioritised action items]
2. [Additional hardening suggestions]
3. [References to OWASP documentation for further reading]
```

If no findings are detected for a severity level, omit that section. If no vulnerabilities are found, state that the scanned code passed the analysis and suggest areas for manual review.

## 6. Severity Classification

- **Critical**: Directly exploitable with high impact — RCE, SQL injection, hardcoded admin credentials, deserialization leading to code execution, prompt injection enabling tool misuse with destructive effects
- **High**: Exploitable under realistic conditions with significant impact — BOLA/IDOR, broken access control bypasses, weak cryptography on sensitive data, authentication bypasses, SSRF to internal metadata
- **Medium**: Requires specific circumstances or has moderate impact — missing security headers, verbose error messages, overly permissive CORS, missing rate limiting on non-critical endpoints, LLM output not sanitised before display
- **Low**: Defence-in-depth issues with minimal direct exploitability — missing SRI attributes, debug logging in non-sensitive areas, informational header leakage, undocumented API versions

When severity is ambiguous, consider: exploitability (how easy), impact (what is at risk), and scope (how much is affected). Err on the side of higher severity for findings involving authentication, authorisation, sensitive data, or AI agent actions with real-world consequences.
