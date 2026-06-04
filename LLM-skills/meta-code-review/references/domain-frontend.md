# Domain overlay — Frontend

Load this file when the changeset contains `.vue`, `.ts` in `web/`, `*_pb.ts`, `vitest.config*`, or FormKit schema files. Extends the generic composition map with frontend-specific lenses, anti-patterns, and ROI gates. Strip all `-B` items for the public port; `-G` items are generic and travel as-is.

## Lens additions
| Scope | Lens | Run via |
|---|---|---|
| XSS / injection in Vue templates | `owasp-top-10` (Web A03) | interactive |
| FormKit schema correctness | `bndry-formkit-schema` skill | interactive |
| Proto TS drift after upstream change | regen + `tsc --noEmit` (no CI gate exists for `web/`) | interactive — mandatory on any proto change |
| Accessibility | axe / manual pass | interactive |

## ROI gates
- Skip generated proto TS files (`*_pb.ts`, `*_connect.ts`) — test behaviour via the generated types, not the codegen output itself.
- Skip FormKit internals — framework-owned; test the schema behaviour, not the library.
- Skip Keycloak OIDC redirect flows — external service.
- Skip CSS utility class coverage — noise with no behavioural signal.
- Skip Pinia store boilerplate that is a thin wrapper over a single Connect call with no logic.

## Anti-patterns

### BNDRY-specific

**FR-B1. Inline styles on FormKit schema nodes**
**Failure:** inline `style` attributes on FormKit schema nodes bypass BNDRY's centralised FormKit theme, creating one-off overrides that drift and conflict with future theme changes.
**Check:** reject any `style:` key on a FormKit schema node. If a default is wrong, fix it in the theme source. Per-instance `style` overrides are never correct.

**FR-B2. Missing `key` on mutually exclusive conditional FormKit sections**
**Failure:** Vue reuses DOM nodes for sibling elements of the same tag; without a `key`, reactive state from the old conditional branch bleeds into the new one.
**Check:** every `$if`/`$else` pair sharing a parent must carry a unique `key`. Child `$formkit` fields inside the branch must also carry `key` — the wrapper key alone is not sufficient.

**FR-B3. Pipe `|` in FormKit `matches` validation regex**
**Failure:** FormKit parses `|` as a rule separator, so `matches:/foo|bar/` silently splits into two broken rules instead of an alternation.
**Check:** no `|` inside a `matches:` regex value. Use character classes or restructure into separate validation rules.

**FR-B4. FormKit behaviour fixed in per-schema workarounds instead of the theme**
**Failure:** unwanted framework defaults papered over with per-instance overrides accumulate into an unmaintainable patchwork that diverges from the theme.
**Check:** if the fix applies to every instance of a component, it belongs in the centralised theme. Per-schema overrides are only valid for genuinely instance-specific variation.

**FR-B5. Proto TS not regenerated after an enum value or field change**
**Failure:** protobuf-es throws at runtime on unrecognised enum values. There is no CI gate for `web/` TS proto drift (only Go has a codegen gate). A new proto enum value passes `tsc` against stale generated unions but fails at runtime.
**Check:** any changeset adding, removing, or renaming a proto enum value, `oneof` variant, or message field must include a `web/` TS regen and a passing `tsc --noEmit`. Enumerate the changed proto symbols and confirm each appears (or is absent) in the regenerated `*_pb.ts`.

**FR-B6. Orphaned Vue consumer after upstream proto symbol deletion (A12 consumer half)**
**Failure:** a deleted proto `oneof` variant or enum value leaves `v-if`/`switch` arms in Vue that type-check against stale generated unions and survive every sweep that doesn't regenerate. A regen is the only reliable signal.
**Check:** a deleted producer symbol is a *trigger*, not the conclusion. Chase it into every `web/` consumer, regenerate TS from current proto, re-run `tsc --noEmit`. The type error the regen surfaces is the orphan. A sweep that never crosses source→regen→consumer will miss this every time.

**FR-B7. PostHog feature flag checked client-side only for access control**
**Failure:** a client-side-only flag gate can be bypassed by JS manipulation. It controls UX visibility, not access. A state-changing Connect RPC gated only in Vue is accessible directly via the API.
**Check:** any flag that controls whether a *mutation* is permitted must be enforced server-side in the Connect handler. Client-side flag = UX only.

**FR-B8. ConnectRPC error codes not mapped to user-facing messages**
**Failure:** swallowing a `connect.CodeNotFound` or `connect.CodePermissionDenied` as a generic UI error hides actionable information and makes failures silent.
**Check:** the Connect error-handling boundary must map canonical error codes to user-facing messages. `CodeInternal` is the only acceptable generic fallback; all other codes need an explicit mapping.

**FR-B9. Keycloak token expiry not handled in long-lived sessions**
**Failure:** access tokens expire; a tab that stays open without a proactive silent-refresh will fail all RPCs after expiry with no user-facing explanation.
**Check:** the auth composable must implement silent refresh before expiry. Verify the refresh interval is less than the token TTL configured in Keycloak.

**FR-B10. Missing loading / error states for async Connect calls**
**Failure:** a component that fires a Connect RPC with no loading skeleton and no error fallback shows blank or stale content during transitions and hides failures silently.
**Check:** every async data fetch must handle three states in the template: loading, error, and success.

**FR-B11. Direct reactive object mutation bypassing Vue's reactivity**
**Failure:** mutating a nested property on a `ref()` (e.g. `ref.value.nested.key = x`) may not trigger reactive updates; the component renders stale data.
**Check:** for `ref`, replace the whole value or affected subtree (`ref.value = { ...ref.value, key: x }`). For `reactive`, direct property assignment is fine. Verify the correct primitive is in use for the data shape.

**FR-B12. Unhandled rejection in `<script setup>` kills the component tree**
**Failure:** a bare `await` without try/catch in `<script setup>` throws an unhandled rejection that propagates up and unmounts ancestors.
**Check:** all async calls in `<script setup>` must be wrapped in try/catch or delegated to `useAsyncData`/`useFetch` with explicit error handling.

**FR-B13. Hardcoded tenant-specific values in shared components**
**Failure:** tenant IDs, feature names, or display strings hardcoded into shared UI components break multi-tenancy when the component is reused across tenants.
**Check:** shared components must derive tenant context from the store or props, never from hardcoded literals.

### Generic

**FR-G1. Unsafe HTML insertion without sanitisation**
**Failure:** `v-html`, `innerHTML`, or `dangerouslySetInnerHTML` with user-controlled content is a direct XSS vector.
**Check:** any dynamic HTML insertion must originate from a server-generated, already-sanitised source, or pass through a DOMPurify-equivalent before render. Prefer text interpolation; treat HTML insertion as a last resort requiring explicit justification.

**FR-G2. Missing Content Security Policy**
**Failure:** no CSP means injected scripts execute without restriction; XSS escalates from nuisance to full session compromise.
**Check:** confirm a CSP header is set (server or meta tag) and restricts `script-src` to known origins. `unsafe-inline` or `unsafe-eval` in `script-src` defeats the policy.

**FR-G3. Client-side access control without server enforcement**
**Failure:** hiding a route or action behind a flag or role check in the frontend is a UX guard, not access control. The API must enforce it independently.
**Check:** for every client-side guard over a *mutation*, confirm the corresponding API endpoint enforces the same restriction server-side.

**FR-G4. Unthrottled reactive watchers causing perf degradation**
**Failure:** a watcher or computed property running expensive work (API calls, large array transforms) on every keystroke or rapid state change degrades responsiveness and can saturate the network.
**Check:** debounce or throttle watchers that trigger external calls. Computed properties should be pure transforms; side effects belong in watchers with appropriate guards.

**FR-G5. Missing error boundaries letting one component crash the tree**
**Failure:** an unhandled error in a leaf component propagates up and unmounts unrelated UI.
**Check:** wrap independently-failing sections in error boundary components. The golden path must never be blocked by a failure in a sidebar widget.

**FR-G6. Generated / framework code tested at the wrong layer**
**Failure:** tests asserting the shape of generated proto types, graphql schemas, or CSS utility classes test the codegen tool, not the application.
**Check:** tests must assert *behaviour* — what the component does with data — not the raw shape of generated types. Generated types are the test fixture, not the subject.

**FR-G7. Missing accessibility on interactive elements**
**Failure:** buttons without `aria-label`, images without `alt`, custom controls without `role`, dialogs without focus management — all fail WCAG and assistive technology users.
**Check:** every interactive element must have an accessible name. Custom controls must declare their `role`. Focus must be managed on modal open and close.

**FR-G8. Hardcoded display strings without i18n coverage**
**Failure:** literals hardcoded in templates are untranslatable and often inconsistent with design-system terminology.
**Check:** all user-facing strings must go through the i18n layer. Grep for string literals in templates not wrapped in `t()` or equivalent.

**FR-G9. Bundle bloat from non-tree-shaken imports**
**Failure:** `import { everything } from 'big-library'` pulls in unused code; per-user JS payload grows without the developer noticing.
**Check:** verify named imports only, or confirm the build tool's tree-shaking is effective for the library. Flag any `import *` from a large dependency.
