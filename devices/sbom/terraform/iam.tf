# IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "device-sbom-audit-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic execution role for CloudWatch logs
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy for S3 access
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "device-sbom-audit-s3-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ManageUploadsPrefix"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.sbom_bucket.arn}/uploads/*"
      },
      {
        # DeleteObject exists solely for the copy-checksum rollback in
        # moveAndDeleteS3Object; validated SBOMs are otherwise write-once.
        Sid    = "WriteOnceArchive"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.sbom_bucket.arn}/sboms/*"
      }
    ]
  })
}

# Allow the Lambda to fetch the two Secrets Manager values it needs at
# runtime. Scoped to exactly the two secret ARNs — no wildcard.
resource "aws_iam_role_policy" "lambda_secrets_policy" {
  name = "device-sbom-audit-secrets-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["secretsmanager:GetSecretValue"]
        Resource = [
          aws_secretsmanager_secret.auth_token.arn,
          aws_secretsmanager_secret.presign_secret.arn,
        ]
      }
    ]
  })
}
