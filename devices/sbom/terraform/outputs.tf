output "lambda_function_url" {
  description = "Lambda function URL for SBOM uploads"
  value       = aws_lambda_function_url.sbom_validator_url.function_url
  sensitive   = false
}

output "s3_bucket_name" {
  description = "S3 bucket name for SBOM storage"
  value       = aws_s3_bucket.sbom_bucket.id
  sensitive   = false
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.sbom_validator.function_name
  sensitive   = false
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for monitoring"
  value       = aws_cloudwatch_log_group.lambda_logs.name
  sensitive   = false
}

output "auth_token_secret_name" {
  description = "Secrets Manager name for the auth token. Fetch the value with `aws secretsmanager get-secret-value --secret-id <name> --query SecretString --output text` when distributing via MDM."
  value       = aws_secretsmanager_secret.auth_token.name
  sensitive   = false
}

output "presign_secret_name" {
  description = "Secrets Manager name for the presign HMAC secret. Fetch the value with `aws secretsmanager get-secret-value --secret-id <name> --query SecretString --output text` when distributing via MDM."
  value       = aws_secretsmanager_secret.presign_secret.name
  sensitive   = false
}

# Token values themselves are deliberately not output. Distribute via
# `aws secretsmanager get-secret-value` so every read is auditable in
# CloudTrail and does not require Terraform state access.

