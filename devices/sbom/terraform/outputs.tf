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

output "auth_token" {
  description = "Authentication token for SBOM uploads. Fetch with `terraform output -raw auth_token` when distributing via MDM."
  value       = random_password.auth_token.result
  sensitive   = true
}

# The presign secret is server-side only and never needs to leave the
# state. We deliberately do not output it; operators do not handle it.

