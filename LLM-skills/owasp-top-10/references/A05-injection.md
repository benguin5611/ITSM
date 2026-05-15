# A05:2025 — Injection

Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. Attacker-supplied data can trick the interpreter into executing unintended commands or accessing data without authorization. This category covers SQL, NoSQL, OS command, LDAP, XSS, and template injection.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-77 | Command Injection |
| CWE-78 | OS Command Injection |
| CWE-79 | Cross-site Scripting (XSS) |
| CWE-89 | SQL Injection |
| CWE-90 | LDAP Injection |
| CWE-94 | Code Injection |
| CWE-917 | Expression Language Injection |
| CWE-943 | Improper Neutralization of Special Elements in Data Query Logic (NoSQL) |

## Detection Patterns

### SQL Injection

**String concatenation in queries — all languages:**
```
["']\s*\+\s*\w+.*(?:SELECT|INSERT|UPDATE|DELETE|WHERE|FROM|JOIN)
(?:SELECT|INSERT|UPDATE|DELETE|WHERE|FROM|JOIN).*["']\s*\+\s*
f["'].*(?:SELECT|INSERT|UPDATE|DELETE|WHERE).*\{
`.*(?:SELECT|INSERT|UPDATE|DELETE|WHERE).*\$\{
```

**JavaScript/TypeScript:**

Vulnerable:
```javascript
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
const query = "SELECT * FROM users WHERE name = '" + userName + "'";
db.query(`DELETE FROM orders WHERE id = ${orderId}`);
```
Secure:
```javascript
const query = 'SELECT * FROM users WHERE id = $1';
db.query(query, [req.params.id]);
// ORM
const user = await User.findByPk(req.params.id);
```

**Python:**

Vulnerable:
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
```
Secure:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# ORM
user = User.objects.get(id=user_id)
```

**Java:**

Vulnerable:
```java
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = conn.createStatement();
stmt.executeQuery(query);
```
Secure:
```java
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
stmt.setInt(1, userId);
```

**Go:**

Vulnerable:
```go
query := fmt.Sprintf("SELECT * FROM users WHERE id = %s", userID)
db.Query(query)
```
Secure:
```go
db.Query("SELECT * FROM users WHERE id = $1", userID)
```

**ORM raw query methods to flag:**
```
\.raw\(|\.rawQuery\(|\.execute\(|Sequelize\.literal\(|knex\.raw\(
RawSQL\(|\.extra\(|connection\.cursor
```

### OS Command Injection

Grep patterns:
```
child_process\.exec\(|execSync\(|spawn\(.*shell.*true
subprocess\.run\(.*shell\s*=\s*True|os\.system\(|os\.popen\(
Runtime\.getRuntime\(\)\.exec\(
exec\.Command\(
```

**JavaScript:**

Vulnerable:
```javascript
const { exec } = require('child_process');
exec(`convert ${req.query.filename} output.png`);
```
Secure:
```javascript
const { execFile } = require('child_process');
execFile('convert', [sanitizedFilename, 'output.png']);
```

**Python:**

Vulnerable:
```python
os.system(f"convert {filename} output.png")
subprocess.run(f"grep {user_input} logs.txt", shell=True)
```
Secure:
```python
subprocess.run(["convert", filename, "output.png"], shell=False)
subprocess.run(["grep", user_input, "logs.txt"])
```

### Cross-Site Scripting (XSS)

Grep patterns:
```
innerHTML|outerHTML|document\.write\(
dangerouslySetInnerHTML
v-html
\{\{!\s|{!!.*!!}
\|safe\b|\|raw\b|\|noescape\b
```

**JavaScript/React:**

Vulnerable:
```javascript
element.innerHTML = userInput;
<div dangerouslySetInnerHTML={{ __html: userContent }} />;
```
Secure:
```javascript
element.textContent = userInput;
// Use a sanitization library
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />;
```

**Template engines:**

Vulnerable:
```python
# Jinja2
return render_template_string(user_template)
# Django
{{ variable|safe }}
```
Secure:
```python
# Jinja2 auto-escapes by default in templates (not render_template_string)
return render_template('page.html', variable=user_input)
# Django — don't use |safe with user input
{{ variable }}
```

### Code Injection

Grep patterns:
```
\beval\(|\bexec\(|\bFunction\(
new Function\(.*\+|eval\(.*\+|eval\(.*\$\{|eval\(.*req\.|eval\(.*request\.
```

Vulnerable:
```javascript
const result = eval(req.body.expression);
const fn = new Function('x', userCode);
```

### NoSQL Injection

Grep patterns:
```
\$where|\$regex|\$ne|\$gt|\$lt
\.find\(\{.*req\.(body|query|params)
```

Vulnerable:
```javascript
db.users.find({ username: req.body.username, password: req.body.password });
// Attacker sends: { "password": { "$ne": "" } }
```
Secure:
```javascript
// Validate and sanitize input types
const username = String(req.body.username);
const password = String(req.body.password);
db.users.find({ username, password: await bcrypt.hash(password, 12) });
```

### LDAP Injection

Grep patterns:
```
ldap\.search\(|ldap_search\(|SearchRequest\(
```
Look for user input concatenated into LDAP filter strings without escaping.

### Template Injection (SSTI)

Grep patterns:
```
render_template_string\(|Template\(.*\+|Template\(.*\$\{|Template\(.*req\.
Velocity\.evaluate\(|freemarker.*\$\{
```

## False Positive Guidance

- `eval()` in build tools, webpack configs, or test fixtures is typically safe
- `innerHTML` setting static content or content from trusted sources (not user input)
- ORM methods like `.find()`, `.findOne()`, `.where()` with object syntax (not string concatenation) are generally safe
- SQL in migration files or seed scripts typically uses hardcoded values
- `dangerouslySetInnerHTML` with content from a sanitization library (DOMPurify) is the intended pattern
- Template rendering with file-based templates (not string-based) auto-escapes by default in most frameworks
