# Domain overlay — Backend

Load this file when the changeset contains `.go`, `.proto`, `sqlc.yaml`, `*.sql` in `db/`, `buf.gen.yaml`, or `buf.work.yaml`. Extends the generic composition map with backend-specific lenses, anti-patterns, and ROI gates.

## Lens additions
| Scope | Lens | Run via |
|---|---|---|
| API injection / auth / access control | `owasp-top-10` (API Security Top 10, API1–API10) | interactive |
| Whole-codebase cross-cutting security | your whole-codebase security-audit skill | workflow (heavy, opt-in) |
| Proto breaking changes | `buf breaking` | interactive — mandatory on any proto change |
| AIP compliance (pagination, filtering, ordering) | AIP lint plugin | interactive |
| Proto API-surface emitter census | A12 two-phase census (producer → consumer) | interactive |
| Query-codegen drift | regenerate + diff | interactive — mandatory on any schema or query change |

## ROI gates
- Skip codegen-generated query wrappers tested directly — test via handler behaviour, not generated functions.
- Skip protobuf marshalling correctness — framework-owned.
- Skip identity-provider OIDC flows — external service.
- Skip pure getter RPC handlers with no logic (no branching, no writes, no auth decisions).
- Do test: auth middleware enforcement, tenant-scoping propagation, audit event emission, pagination enforcement, transaction correctness.

## Anti-patterns

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
