variable "s3_bucket_name" {
  description = "S3 bucket name for SBOM storage. MUST be overridden — S3 names are globally unique, so the placeholder default will fail to create. Choose a name your org owns (e.g. device-sbom-audit.security.example.com). The access-logs bucket is derived as <s3_bucket_name>-access-logs."
  type        = string
  default     = "device-sbom-audit.example.com"
}

variable "aws_region" {
  description = "AWS region for all resources in this stack."
  type        = string
  default     = "ap-southeast-2"
}

variable "lambda_reserved_concurrency" {
  description = "Reserved concurrency for the Lambda. Enter 0 on a fresh AWS account (account-wide concurrency minimum is 10 by default, so reserving any is rejected). Enter 10 on a mature production account."
  type        = number

  validation {
    condition     = contains([0, 10], var.lambda_reserved_concurrency)
    error_message = "Must be 0 (new/personal account — no reservation) or 10 (mature account)."
  }
}

variable "alert_email" {
  description = "Email address to receive CloudWatch alarm notifications. Leave empty to skip the SNS subscription and keep terraform plan diff-free."
  type        = string
  default     = ""
}
