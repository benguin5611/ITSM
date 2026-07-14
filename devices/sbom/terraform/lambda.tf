# Generate authentication secrets.
#
# Restrict the special-char set to characters that survive shell-quoted
# contexts, HTTP header values, and curl --config file parsing without
# escaping surprises. The default special-char set includes `!`, `$`,
# `&`, `*`, and `?`, all of which can cause silent fleet-availability
# bugs when interpolated through bash, curl config files, or future
# refactors that drop into eval/echo.
#
# 64 chars × 66-char alphabet ≈ 387 bits of entropy, comfortably above
# what HMAC-SHA256 or any practical bearer token needs.
resource "random_password" "auth_token" {
  length           = 64
  special          = true
  override_special = "-_.~"
}

resource "random_password" "presign_secret" {
  length           = 64
  special          = true
  override_special = "-_.~"
}

# Build Lambda binary
resource "null_resource" "lambda_build" {
  triggers = {
    go_source_hash = filesha256("${path.module}/../lambda-spdx-validator.go")
    schema_hash    = filesha256("${path.module}/../spdx-2.3-schema.json")
    go_mod_hash    = filesha256("${path.module}/../go.mod")
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -euo pipefail
      if [ "$(id -u)" = "0" ]; then
        echo "Refusing to build as root — running 'go build' under sudo pollutes ~/go with root-owned files." >&2
        echo "Re-run terraform apply as your normal user." >&2
        exit 1
      fi
      cd ${path.module}/..
      echo "Building Lambda binary..."
      mkdir -p terraform/build terraform/.gocache/pkg/mod
      GOOS=linux GOARCH=arm64 CGO_ENABLED=0 \
        GOPATH="$PWD/terraform/.gocache" \
        GOMODCACHE="$PWD/terraform/.gocache/pkg/mod" \
        go build -o terraform/build/bootstrap lambda-spdx-validator.go
      cp spdx-2.3-schema.json terraform/build/
      echo "Lambda binary built successfully"
    EOT
  }
}

# Create zip file of Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build"
  output_path = "${path.module}/lambda-spdx-validator.zip"

  depends_on = [null_resource.lambda_build]
}

# Lambda function
resource "aws_lambda_function" "sbom_validator" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "bootstrap"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  runtime                        = "provided.al2023"
  architectures                  = ["arm64"]
  timeout                        = 120
  memory_size                    = 512
  reserved_concurrent_executions = var.lambda_reserved_concurrency == 0 ? -1 : var.lambda_reserved_concurrency

  environment {
    variables = {
      SBOM_BUCKET                = aws_s3_bucket.sbom_bucket.id
      SBOM_AUTH_TOKEN_SECRET_ARN = aws_secretsmanager_secret.auth_token.arn
      SBOM_PRESIGN_SECRET_ARN    = aws_secretsmanager_secret.presign_secret.arn
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_s3_policy,
    aws_cloudwatch_log_group.lambda_logs
  ]
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.logs.arn
}

# Lambda function URL
resource "aws_lambda_function_url" "sbom_validator_url" {
  function_name      = aws_lambda_function.sbom_validator.function_name
  authorization_type = "NONE"
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sbom_validator.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.sbom_bucket.arn
}

# Permission for public access to Function URL
resource "aws_lambda_permission" "function_url_invoke" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.sbom_validator.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

# Function URLs created after October 2025 also require lambda:InvokeFunction
# alongside lambda:InvokeFunctionUrl; without it fresh deploys return 403.
# invoked_via_function_url scopes the grant to calls made through the URL,
# so this does not open up direct Invoke API access.
resource "aws_lambda_permission" "function_url_invoke_function" {
  statement_id             = "FunctionURLInvokeAllowPublicAccess"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.sbom_validator.function_name
  principal                = "*"
  invoked_via_function_url = true
}
