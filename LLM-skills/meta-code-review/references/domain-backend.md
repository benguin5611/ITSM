# Domain overlay — Backend

Load this file when the changeset contains `.go`, `.proto`, `sqlc.yaml`, `*.sql` in `db/`, `buf.gen.yaml`, or `buf.work.yaml`. Extends the generic composition map with backend-specific lenses, anti-patterns, and ROI gates. Strip all `-B` items for the public port; `-G` items are generic and travel as-is.

## Lens additions
| Scope | Lens | Run via |
|---|---|---|
| API injection / auth / access control | `owasp-top-10` (API Security Top 10, API1–API10) | interactive |
| Whole-codebase cross-cutting security | `security-audit-bndry` | workflow (heavy, opt-in) |
| Proto breaking changes | `buf breaking` | interactive — mandatory on any proto change |
| AIP compliance (pagination, filtering, ordering) | `buf-plugin-aip` lint | interactive |
| Proto API-surface emitter census | A12 two-phase census (producer → consumer) | interactive |
| sqlc drift | `sqlc generate` + diff | interactive — mandatory on any schema or query change |

## ROI gates
- Skip sqlc-generated query wrappers tested directly — test via handler behaviour, not generated functions.
- Skip protobuf marshalling correctness — framework-owned.
- Skip Keycloak OIDC flows — external service.
- Skip pure getter RPC handlers with no logic (no branching, no writes, no auth decisions).
- Do test: auth middleware enforcement, RLS GUC propagation, audit event emission, pagination enforcement, transaction correctness.

## Anti-patterns

### BNDRY-specific

**BE-B1. Missing `app.tenant` GUC before a tenant-scoped query**
**Failure:** every query on tenant-scoped tables is protected by Postgres RLS only if `SET app.tenant = <id>` precedes it on the connection. A handler that queries without setting the GUC operates without RLS and can return or modify cross-tenant data.
**Check:** every Connect handler touching tenant-scoped tables must set `app.tenant` before the first query. Trace the propagation chain: interceptor → context → query helper → GUC set. A missing `SET` is a data-isolation defect.

**BE-B2. Tenant ID not propagated through goroutines spawned inside a handler**
**Failure:** `iam.TenantIDFromContext()` reads from the request context. A goroutine spawned with `context.Background()` or a bare `go func()` loses the tenant binding; any query it runs has no tenant GUC.
**Check:** every goroutine spawned inside a request handler must inherit the request context (or a derived context), not `context.Background()`. Trace the context through any channel, worker pool, or async dispatch.

**BE-B3. Connect RPC registered without auth/IAM interceptor**
**Failure:** a handler registered without the auth interceptor applied is reachable without authentication. Common vectors: new handlers added before the chain is wired, "internal" RPCs accidentally exposed, refactors that copy registration without middleware.
**Check:** enumerate every handler registration. Every RPC must have the interceptor chain applied. For genuinely public RPCs, confirm the absence of auth is a documented, reviewed decision and that rate limiting is applied.

**BE-B4. sqlc-generated code not regenerated after schema or query change**
**Failure:** sqlc produces type-safe query wrappers; a schema migration or query edit without re-running `sqlc generate` leaves generated code stale. The codegen gate runs per-module — confirm it runs for every module with its own `sqlc.yaml`, since each may have a different sqlc version pin.
**Check:** any changeset touching `*.sql`, migration files, or `sqlc.yaml` must include a `sqlc generate` run and a clean diff. Verify the correct sqlc version is used per module (root and sub-modules may differ).

**BE-B5. Proto field number reused after deprecation**
**Failure:** reusing a wire field number — even one that only existed on an internal branch — is a breaking wire-format change. A client that cached the old message will misparse the new field.
**Check:** deprecated fields must be marked `deprecated = true` and their numbers added to `reserved`. Never assign a new semantic to a previously-used field number. `buf breaking` does not catch intra-branch reuse — manually audit field numbers in the changeset.

**BE-B6. Proto `oneof` variants / `enum` values with zero non-generated emitters**
**Failure:** audit event constants and `oneof` variants are the highest-risk surface. Generated marshalling references every defined symbol, so reachability tools (`deadcode`, staticcheck) report them live. An audit event defined but never emitted in hand-written code is dead — and ships into the published API contract.
**Check:** run a deterministic emitter census: enumerate every proto `oneof` variant, `enum` value, and audit-event constant in the changeset; count non-generated, non-test constructors. Zero = dead candidate. Trigger hardest when the changeset moves a capability from one event path to another — the old path's constants become orphans. See anti-pattern A12 for the full method.

**BE-B7. Missing protovalidate rules on user-controlled proto fields**
**Failure:** protovalidate is the validation layer; a missing `required`, length bound, or pattern constraint on a user-supplied field lets raw input reach the handler.
**Check:** every proto `rpc` input message field accepting user-controlled data must have `validate.rules` annotations. Minimum: `required` for mandatory fields, `string.max_len` for free-text, `string.pattern` or an enum for structured values.

**BE-B8. squirrel `Expr()` with user-controlled input**
**Failure:** squirrel's typed builders (`Eq`, `Like`, `ILike`, etc.) use parameterised queries. `Expr("column = '" + userValue + "'")` or raw SQL concatenation bypasses parameterisation — direct SQL injection.
**Check:** audit every `Expr()` call in the changeset. Any `Expr` whose argument is constructed from user input is a defect. Use typed squirrel builders for all user-supplied values.

**BE-B9. Listing RPC without pagination (AIP-132 non-compliance)**
**Failure:** an unbounded listing query is a DoS vector and a perf risk at scale. AIP-132 mandates `page_size` / `page_token`; `buf-plugin-aip` lints for this.
**Check:** every `List*` RPC must implement `page_size` and `page_token`. `buf-plugin-aip` catches the proto gap; verify the handler also enforces a `max_page_size` cap on the Go side.

**BE-B10. Audit event emitted at wrong scope**
**Failure:** activity logs are entity-scoped via `EntityResourceIDs`. An audit event emitted to a workspace scope or any other scope does not appear in the entity's activity timeline — the consumer shows nothing.
**Check:** every audit event emission must reference the correct `EntityResourceIDs`. Verify the resource type matches the entity being mutated.

**BE-B11. State-changing RPC missing an audit event**
**Failure:** any RPC that transitions entity state (create, update, delete, link, status transition) without a corresponding audit event is a compliance and debuggability gap.
**Check:** enumerate every state-changing RPC in the changeset. Confirm a matching audit event constant exists, has a non-zero emitter count from the census, and is emitted on the success path — not only in tests.

**BE-B12. Honeycomb instrumentation missing on new Connect handlers**
**Failure:** the base ConnectRPC interceptor adds request-level attributes; handler-level attributes (tenant ID, entity type, operation result) are the developer's responsibility. A new handler without them produces traces with no operational context.
**Check:** every new Connect handler must add at minimum: tenant ID, the primary entity being operated on, and the result (success / error code). Use an existing instrumented handler as the reference.

**BE-B13. N+1 query pattern in a handler**
**Failure:** fetching a list then querying per-item inside a loop scales linearly with result count. sqlc's type safety doesn't catch it; it requires reading handler logic against the query set.
**Check:** any handler iterating a query result and issuing a query inside the loop is an N+1. Use sqlc batch queries, a JOIN, or an `IN (...)` clause.

**BE-B14. Context cancellation not propagated to DB queries**
**Failure:** passing `context.Background()` to a DB call means the query runs to completion after client disconnect or request timeout, holding a connection pool slot.
**Check:** every DB call in a request handler must use the request context or a derived, deadline-bounded context. `context.Background()` inside a request handler is always suspect.

**BE-B15. Missing transaction for multi-step state transitions**
**Failure:** an RPC that writes to multiple tables without a transaction leaves the DB inconsistent on partial failure.
**Check:** any handler writing to more than one table on the success path must wrap those writes in a transaction. Partial success is not an acceptable outcome for state transitions.

**BE-B16. Missing rate limiting on unauthenticated / public-facing RPCs**
**Failure:** any Connect RPC reachable without a Keycloak token is a DoS and credential-stuffing surface without rate limiting.
**Check:** enumerate every RPC registered without the auth interceptor. Each must have rate-limiting middleware applied and confirmed at the Connect layer, not only at the infrastructure edge.

**BE-B17. KMS key ID or AWS resource identifier hardcoded in source**
**Failure:** hardcoded KMS key IDs or ARNs make key rotation a code deploy and expose identifiers in version history.
**Check:** KMS key IDs, ARNs, and other AWS resource identifiers must come from config or env vars. No literal `arn:aws:kms:...` or `key-*` strings in Go source.

### Generic

**BE-G1. SQL injection via raw query fragments**
**Failure:** string concatenation or interpolation of user-controlled values into a SQL string bypasses parameterisation.
**Check:** every dynamic query accepting user input must use parameterised placeholders. Any raw fragment builder call or `fmt.Sprintf` into SQL is a manual audit point.

**BE-G2. Missing auth enforcement on an endpoint**
**Failure:** a handler reachable without authentication is a full access-control bypass.
**Check:** enumerate every registered handler. Every one must have auth enforced, or the absence must be a documented, reviewed decision with compensating controls.

**BE-G3. Missing pagination on list endpoints**
**Failure:** an unbounded list query is a DoS vector and a perf risk at scale.
**Check:** every list endpoint must accept a page size and return a continuation token. Enforce a maximum page size cap in the handler, not only in the proto/schema.

**BE-G4. N+1 query pattern**
**Failure:** a query per row in a result set scales linearly; at modest data sizes it exceeds acceptable latency.
**Check:** any handler iterating a query result and issuing a query inside the loop is an N+1. Prefer batch queries, JOINs, or `IN (...)` clauses.

**BE-G5. `context.Background()` inside a request handler**
**Failure:** loses cancellation, deadline, and trace context — the query runs after client disconnect, and the trace loses its span hierarchy.
**Check:** every DB call, outbound RPC, and goroutine inside a request handler must use the request context or a derived context.

**BE-G6. Missing transaction for multi-step writes**
**Failure:** a partial failure mid-handler leaves the DB in an inconsistent state.
**Check:** any handler writing to more than one table must wrap the writes in a transaction.

**BE-G7. Goroutine leak in a handler**
**Failure:** a goroutine launched without an exit signal runs indefinitely after the request completes, holding resources and accumulating over time.
**Check:** every goroutine spawned inside a handler must have a clear exit condition tied to the request context's cancellation.

**BE-G8. Wrong error code returned across boundaries**
**Failure:** returning `Internal` for a not-found or invalid-argument condition maps to the wrong HTTP status and confuses clients and monitoring.
**Check:** map every error exit to the correct canonical code. `Internal` is for unexpected failures only; all user-caused failures have a more specific code.

**BE-G9. Input validation only at the application layer, not the API boundary**
**Failure:** validation that lives only in business logic can be bypassed by direct API calls. The boundary must independently validate all inputs.
**Check:** every API input field accepting user-controlled data must be validated at the schema/proto layer before it reaches handler logic.

**BE-G10. Hardcoded configuration values**
**Failure:** hardcoded limits, identifiers, feature flags, or resource names make configuration a code deploy and expose values in version history.
**Check:** externally-meaningful values must come from config or environment, not source literals.

**BE-G11. Error swallowing without the underlying cause**
**Failure:** logging "operation failed" and returning a generic error destroys the diagnostic chain; the original error is unrecoverable in production.
**Check:** every error return must either propagate the wrapped original error or log it with enough context to reconstruct the failure path.

**BE-G12. Generated code not regenerated after a schema change**
**Failure:** ORM, codegen, or proto-generated code that drifts from its source of truth type-checks fine but fails at runtime or produces wrong results.
**Check:** any changeset touching the source of truth for generated code (schema, proto, query file) must include a regeneration run and a clean diff.
