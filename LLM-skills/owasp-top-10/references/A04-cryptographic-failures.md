# A04:2025 — Cryptographic Failures

Cryptographic failures occur when sensitive data is exposed due to weak or missing cryptography — broken algorithms, hardcoded keys, missing encryption in transit or at rest, or improper random number generation.

## CWE Mappings

| CWE | Name |
|-----|------|
| CWE-261 | Weak Encoding for Password |
| CWE-296 | Improper Following of a Certificate's Chain of Trust |
| CWE-310 | Cryptographic Issues |
| CWE-319 | Cleartext Transmission of Sensitive Information |
| CWE-321 | Use of Hard-coded Cryptographic Key |
| CWE-326 | Inadequate Encryption Strength |
| CWE-327 | Use of a Broken or Risky Cryptographic Algorithm |
| CWE-328 | Use of Weak Hash |
| CWE-330 | Use of Insufficiently Random Values |
| CWE-759 | Use of One-Way Hash without a Salt |

## Detection Patterns

### Weak Algorithms

Grep patterns:
```
MD5|md5|SHA1|sha1|DES|des|RC4|rc4|ECB|ecb|Blowfish
createHash\(["']md5|createHash\(["']sha1
hashlib\.md5|hashlib\.sha1
MessageDigest\.getInstance\(["']MD5|MessageDigest\.getInstance\(["']SHA-1
```

**Note**: MD5/SHA1 are acceptable for non-security purposes (checksums, cache keys, ETags). Flag only when used for passwords, signatures, tokens, or integrity verification of sensitive data.

### Hardcoded Secrets

Grep patterns:
```
(?i)(password|secret|key|token|api_key|apikey|private_key)\s*[=:]\s*["'][^"']{8,}
-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
AKIA[0-9A-Z]{16}
```

### JavaScript / TypeScript

Vulnerable:
```javascript
const hash = crypto.createHash('md5').update(password).digest('hex');
const token = Math.random().toString(36).substring(2);
const key = 'hardcoded-secret-key-12345';
```
Secure:
```javascript
const hash = await bcrypt.hash(password, 12);
const token = crypto.randomBytes(32).toString('hex');
const key = process.env.SECRET_KEY;
```

**Weak random for security:**
```
grep -n "Math\.random\(\)"
```
Flag when used for tokens, IDs, passwords, or any security-sensitive value. `crypto.randomBytes()` or `crypto.randomUUID()` should be used instead.

### Python

Vulnerable:
```python
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()
token = str(random.randint(100000, 999999))
```
Secure:
```python
from passlib.hash import argon2
hashed = argon2.hash(password)
token = secrets.token_urlsafe(32)
```

**Grep patterns:**
```
random\.random\(\)|random\.randint\(|random\.choice\(
```
Flag when used for security. `secrets` module should be used instead.

### Java

Vulnerable:
```java
MessageDigest md = MessageDigest.getInstance("MD5");
SecureRandom sr = new SecureRandom(fixedSeed);
Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
```
Secure:
```java
MessageDigest md = MessageDigest.getInstance("SHA-256");
SecureRandom sr = new SecureRandom();
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
```

### Go

Vulnerable:
```go
h := md5.Sum([]byte(password))
key := []byte("hardcoded-key")
block, _ := des.NewCipher(key)
```
Secure:
```go
hash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
key := os.Getenv("ENCRYPTION_KEY")
block, _ := aes.NewCipher(keyBytes)
```

## Key Strength Requirements

| Algorithm | Minimum Secure Key Size |
|-----------|------------------------|
| RSA | 2048 bits (3072+ recommended) |
| ECC | 256 bits |
| AES | 128 bits (256 recommended) |
| HMAC | 256 bits |

## Recommended Algorithms (2025)

| Purpose | Recommended | Avoid |
|---------|------------|-------|
| Password hashing | Argon2id, bcrypt, scrypt | MD5, SHA1, SHA256 (unsalted) |
| General hashing | SHA-256, SHA-3, BLAKE3 | MD5, SHA1 |
| Symmetric encryption | AES-256-GCM, ChaCha20-Poly1305 | DES, 3DES, RC4, AES-ECB |
| Asymmetric encryption | RSA-OAEP (2048+), ECIES | RSA-PKCS1v1.5 |
| Digital signatures | Ed25519, ECDSA (P-256+), RSA-PSS | DSA, RSA-PKCS1v1.5 |
| Random generation | OS CSPRNG (crypto.randomBytes, secrets, SecureRandom) | Math.random, random module |

## Missing Encryption in Transit

Grep patterns:
```
http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)
verify\s*=\s*False|InsecureSkipVerify.*true|NODE_TLS_REJECT_UNAUTHORIZED.*0
```

## False Positive Guidance

- MD5/SHA1 for non-security checksums (file deduplication, cache keys, ETags) is acceptable
- `Math.random()` for UI purposes (animations, shuffling display order) is fine
- Test fixtures with hardcoded "secrets" are expected — check if the file is in a test directory
- Base64 encoding is not encryption but is sometimes mistaken for it; flag only if used as a security measure
- Environment variable references (`process.env.KEY`) are the pattern we want to see, not flag
