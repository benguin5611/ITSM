# A03:2025 — Software Supply Chain Failures

Software supply chain failures encompass weaknesses related to dependencies, build systems, and distribution — the entire ecosystem that delivers software beyond just your code. This expanded category (renamed from "Vulnerable and Outdated Components" in 2021) now covers dependency management, build pipeline integrity, and artifact distribution.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-426 | Untrusted Search Path |
| CWE-829 | Inclusion of Functionality from Untrusted Control Sphere |
| CWE-937 | Using Components with Known Vulnerabilities |
| CWE-1104 | Use of Unmaintained Third-Party Components |
| CWE-1357 | Reliance on Insufficiently Trustworthy Component |

## Detection Patterns

### Dependency Pinning

**npm / yarn:**
```
grep -n '"\*"\|"latest"\|">=\|">\|"~\|"\^' package.json
```
Check `package-lock.json` or `yarn.lock` exists and contains integrity hashes:
```
grep -n "integrity" package-lock.json | head -5
```

Flag: `*`, `latest`, or no lockfile present. Acceptable: `^` and `~` in `package.json` when a lockfile exists with integrity hashes.

**Python:**
```
grep -n ">=\|~=" requirements.txt
```
Check for `--require-hashes` in pip install commands or hash pinning in requirements.

**Go:**
Check `go.sum` exists alongside `go.mod`.

**Java:**
Check for version ranges in `pom.xml` — versions should be exact.

### Malicious Install Scripts

**npm:**
```
grep -n "preinstall\|postinstall\|preuninstall\|postuninstall" package.json
```
Examine any install scripts for:
- Network calls (`curl`, `wget`, `fetch`, `http`)
- File system writes outside node_modules
- Environment variable exfiltration
- Obfuscated code (Base64 decoding, eval)

### CI/CD Pipeline Security

**GitHub Actions:**
```
grep -rn "uses:.*@main\|uses:.*@master\|uses:.*@dev" .github/workflows/
```
Flag actions pinned to branch names instead of SHA hashes or version tags.

Vulnerable:
```yaml
uses: actions/checkout@main
```
Secure:
```yaml
uses: actions/checkout@v4  # or SHA: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

**Injectable workflow variables:**
```
grep -rn "\$\{\{.*github\.event\.\(issue\|pull_request\|comment\).*\}\}" .github/workflows/
```
Flag user-controlled event data injected into `run:` steps without sanitisation.

**Secrets in CI:**
```
grep -rn "echo.*\$\{\{.*secrets\.\|>> \$GITHUB_ENV.*\$\{\{.*secrets\." .github/workflows/
```
Flag secrets written to environment files or echoed to output.

### Lockfile Integrity

Check that lockfiles are committed and not in `.gitignore`:
```
grep -n "package-lock\|yarn\.lock\|Pipfile\.lock\|go\.sum\|Cargo\.lock\|composer\.lock" .gitignore
```
Flag any lockfile in `.gitignore`.

### Known Vulnerabilities

Note: Static analysis cannot detect all known CVEs, but check for:
- Extremely outdated major versions in lockfiles
- Dependencies with known, widely-publicized vulnerabilities
- Recommend running `npm audit`, `pip-audit`, `govulncheck`, `cargo audit`, or `mvn dependency-check:check`

### Typosquatting Risk

Check for packages with names similar to popular packages but with:
- Transposed characters
- Missing/extra characters
- Different separators (`lodash` vs `l0dash`, `colors` vs `colour`)

### Subresource Integrity (SRI)

For CDN-loaded scripts in HTML:
```
grep -rn "<script.*src=.*http\|<link.*href=.*http" --include="*.html"
```
Check for `integrity` attribute on external resources.

Vulnerable:
```html
<script src="https://cdn.example.com/lib.js"></script>
```
Secure:
```html
<script src="https://cdn.example.com/lib.js" integrity="sha384-..." crossorigin="anonymous"></script>
```

## Remediation Summary

| Issue | Fix |
|-------|-----|
| Unpinned dependencies | Use exact versions + lockfile with integrity hashes |
| Actions on branch refs | Pin to SHA hash or version tag |
| Missing lockfile | Generate and commit lockfile |
| Suspicious install scripts | Audit scripts, consider `--ignore-scripts` with explicit allowlist |
| No vulnerability scanning | Add `npm audit` / `pip-audit` / equivalent to CI |
| Missing SRI | Add integrity attributes to CDN resources |

## False Positive Guidance

- `^` and `~` in `package.json` are standard when a lockfile exists — the lockfile provides exact pinning
- Development-only dependencies (`devDependencies`) have lower risk but should still be pinned
- First-party/internal packages with version ranges may be intentional for monorepo setups
- GitHub Actions by the `actions/` org with version tags (e.g., `@v4`) are generally safe, though SHA pinning is stricter
