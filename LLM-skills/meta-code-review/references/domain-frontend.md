# Domain overlay — Frontend

Load this file when the changeset contains `.vue`, `.ts` in `web/`, `*_pb.ts`, `vitest.config*`, or FormKit schema files. Extends the generic composition map with frontend-specific lenses, anti-patterns, and ROI gates.

## Lens additions
| Scope | Lens | Run via |
|---|---|---|
| XSS / injection in templates | `owasp-top-10` (Web A03) | interactive |
| Form-schema correctness | your project's form-schema skill (if present) | interactive |
| Generated-types drift after upstream change | regen + `tsc --noEmit` | interactive — mandatory on any schema/proto change |
| Accessibility | axe / manual pass | interactive |

## ROI gates
- Skip generated type files (`*_pb.ts`, `*_connect.ts`) — test behaviour via the generated types, not the codegen output itself.
- Skip form-framework internals — framework-owned; test the schema behaviour, not the library.
- Skip identity-provider OIDC redirect flows — external service.
- Skip CSS utility class coverage — noise with no behavioural signal.
- Skip store boilerplate that is a thin wrapper over a single API call with no logic.

## Anti-patterns

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
