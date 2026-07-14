# A01:2025 — Broken Access Control

Broken access control is the most prevalent OWASP category. It occurs when users can act outside their intended permissions — accessing other users' data, modifying records they shouldn't, or escalating privileges.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-200 | Exposure of Sensitive Information to an Unauthorized Actor |
| CWE-284 | Improper Access Control |
| CWE-285 | Improper Authorization |
| CWE-352 | Cross-Site Request Forgery (CSRF) |
| CWE-639 | Authorization Bypass Through User-Controlled Key (IDOR) |
| CWE-862 | Missing Authorization |
| CWE-863 | Incorrect Authorization |
| CWE-918 | Server-Side Request Forgery (SSRF) — consolidated into A01 in 2025 |

## Detection Patterns

### JavaScript / TypeScript (Express, Next.js, Fastify)

**Missing auth middleware on routes:**
```
grep -n "app\.(get|post|put|patch|delete)\(" routes/
```
Look for route handlers that lack an authentication/authorisation middleware parameter between the path and handler function.

Vulnerable:
```javascript
app.get('/api/users/:id', (req, res) => { ... });
```
Secure:
```javascript
app.get('/api/users/:id', authenticate, authorize('user:read'), (req, res) => { ... });
```

**Insecure Direct Object Reference (IDOR):**
```
grep -n "req\.params\.\|req\.query\.\|req\.body\." handlers/
```
Look for database lookups using user-supplied IDs without ownership validation:

Vulnerable:
```javascript
const order = await Order.findById(req.params.orderId);
```
Secure:
```javascript
const order = await Order.findOne({ _id: req.params.orderId, userId: req.user.id });
```

**CORS misconfiguration:**
```
grep -n "Access-Control-Allow-Origin\|cors("
```
Vulnerable:
```javascript
app.use(cors({ origin: '*', credentials: true }));
```
Secure:
```javascript
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
```

**SSRF patterns (consolidated from former A10:2021):**
```
grep -n "fetch(\|axios\.\|http\.get\|https\.get\|request("
```
Look for user-controlled URLs passed to HTTP clients without allowlist validation.

### Python (Django, Flask, FastAPI)

**Missing authorisation decorators:**
```
grep -n "def \w\+.*request" views.py
```
Look for view functions missing `@login_required`, `@permission_required`, or equivalent.

Vulnerable:
```python
def user_profile(request, user_id):
    return User.objects.get(id=user_id)
```
Secure:
```python
@login_required
@permission_required('users.view_user')
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id, organization=request.user.organization)
    return user
```

**Django: missing CSRF protection:**
```
grep -n "@csrf_exempt"
```
Flag any `@csrf_exempt` on state-changing endpoints.

**FastAPI: missing dependency injection for auth:**
```
grep -n "@app\.\(get\|post\|put\|delete\)"
```
Look for endpoints without `Depends(get_current_user)` or similar.

### Java (Spring Boot)

**Missing security annotations:**
```
grep -n "@RequestMapping\|@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping"
```
Look for controller methods missing `@PreAuthorize`, `@Secured`, or `@RolesAllowed`.

Vulnerable:
```java
@GetMapping("/admin/users")
public List<User> getAllUsers() { ... }
```
Secure:
```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public List<User> getAllUsers() { ... }
```

### Go (net/http, Gin, Echo)

**Missing middleware on route groups:**
```
grep -n "\.GET\|\.POST\|\.PUT\|\.DELETE\|HandleFunc"
```
Look for routes registered outside authenticated groups or without auth middleware.

**Path traversal via file serving:**
```
grep -n "http\.ServeFile\|filepath\.Join.*req"
```
Look for user-controlled paths passed to file-serving functions without sanitisation.

## General Patterns (All Languages)

- **Horizontal privilege escalation**: User A accessing User B's resources via predictable IDs
- **Vertical privilege escalation**: Regular user accessing admin functions
- **Path traversal**: `../` sequences in file access operations
- **Missing CSRF tokens**: State-changing operations (POST/PUT/DELETE) without anti-CSRF measures
- **Metadata manipulation**: JWT claims, cookies, or hidden fields used for access decisions without server-side validation
- **Force browsing**: Admin pages accessible without authentication (e.g., `/admin`, `/dashboard`)

## False Positive Guidance

- Public endpoints (login, registration, health checks, public API docs) legitimately skip auth
- Internal-only services behind a network boundary may use lighter auth — still flag but note the context
- GraphQL introspection endpoints are often intentionally public in development
- Static asset routes (`/public/`, `/static/`, `/assets/`) typically don't need auth
- CORS `origin: *` is acceptable when `credentials: false` (public APIs without cookies)
