# Both secrets live in Secrets Manager rather than Lambda env vars so:
#  - reading the value requires secretsmanager:GetSecretValue (scopable
#    per-secret) rather than the broader lambda:GetFunctionConfiguration
#  - every read is logged to CloudTrail
#  - rotation is a one-call operation, not a Lambda env-var update + redeploy

resource "aws_secretsmanager_secret" "auth_token" {
  name        = "device-sbom-audit/auth-token"
  description = "Shared bearer token distributed to managed devices via MDM"
  # Allow re-create after destroy with the same name; the 7-day default
  # recovery window would block iteration during development.
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "auth_token" {
  secret_id     = aws_secretsmanager_secret.auth_token.id
  secret_string = random_password.auth_token.result
}

resource "aws_secretsmanager_secret" "presign_secret" {
  name                    = "device-sbom-audit/presign-secret"
  description             = "HMAC secret for binding S3 uploads to authenticated presign operations (server-side only)"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "presign_secret" {
  secret_id     = aws_secretsmanager_secret.presign_secret.id
  secret_string = random_password.presign_secret.result
}
