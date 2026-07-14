# Both secrets live in Secrets Manager rather than Lambda env vars so:
#  - reading the value requires secretsmanager:GetSecretValue (scopable
#    per-secret) rather than the broader lambda:GetFunctionConfiguration
#  - every read is logged to CloudTrail
#  - rotation is a one-call operation, not a Lambda env-var update + redeploy
#
# Caveat: because the values come from random_password and are written via
# aws_secretsmanager_secret_version, both plaintext secrets also sit in the
# Terraform state file. Protect the state as you would the secrets themselves.

resource "aws_secretsmanager_secret" "auth_token" {
  name        = "device-sbom-audit/auth-token"
  description = "Shared bearer token distributed to managed devices via MDM"
  # Dev-only trade-off: 0 deletes the secret immediately on destroy so the
  # name can be reused straight away. Any recovery window (default 30 days)
  # blocks re-creating a secret with the same name until it elapses. In
  # production, prefer a recovery window over unrecoverable deletes.
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "auth_token" {
  secret_id     = aws_secretsmanager_secret.auth_token.id
  secret_string = random_password.auth_token.result
}

resource "aws_secretsmanager_secret" "presign_secret" {
  name        = "device-sbom-audit/presign-secret"
  description = "HMAC secret for binding S3 uploads to authenticated presign operations (server-side only)"
  # See auth_token above: dev-only immediate delete for name reuse.
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "presign_secret" {
  secret_id     = aws_secretsmanager_secret.presign_secret.id
  secret_string = random_password.presign_secret.result
}
