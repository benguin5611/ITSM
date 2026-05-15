# S3 bucket for SBOM storage
resource "aws_s3_bucket" "sbom_bucket" {
  bucket = "device-sbom-audit.security.example.com"
}

# Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "sbom_bucket_encryption" {
  bucket = aws_s3_bucket.sbom_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Bucket versioning
resource "aws_s3_bucket_versioning" "sbom_bucket_versioning" {
  bucket = aws_s3_bucket.sbom_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "sbom_bucket_lifecycle" {
  bucket = aws_s3_bucket.sbom_bucket.id

  rule {
    id     = "CleanupUploads"
    status = "Enabled"

    filter {
      prefix = "uploads/"
    }

    expiration {
      days = 1
    }

    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }

  rule {
    id     = "ArchiveAndExpire"
    status = "Enabled"

    filter {
      prefix = "sboms/"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "sbom_bucket_pab" {
  bucket = aws_s3_bucket.sbom_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Disable ACLs entirely — bucket owner is sole authority
resource "aws_s3_bucket_ownership_controls" "sbom_bucket_ownership" {
  bucket = aws_s3_bucket.sbom_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Defense-in-depth bucket policy.
data "aws_iam_policy_document" "sbom_bucket_policy" {
  statement {
    sid       = "DenyCrossAccountAccess"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.sbom_bucket.arn, "${aws_s3_bucket.sbom_bucket.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "StringNotEquals"
      variable = "aws:PrincipalAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  statement {
    sid       = "DenyInsecureTransport"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.sbom_bucket.arn, "${aws_s3_bucket.sbom_bucket.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  statement {
    sid       = "DenyUnencryptedUploads"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.sbom_bucket.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["AES256"]
    }
  }

  # Only the Lambda execution role may write to uploads/ — blocks any
  # other in-account principal from putting objects directly.
  statement {
    sid       = "DenyDirectUploadsExceptLambda"
    effect    = "Deny"
    actions   = ["s3:PutObject", "s3:PutObjectAcl"]
    resources = ["${aws_s3_bucket.sbom_bucket.arn}/uploads/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "StringNotLike"
      variable = "aws:userId"
      values = [
        "${aws_iam_role.lambda_role.unique_id}:*",
        data.aws_caller_identity.current.account_id,
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "sbom_bucket_policy" {
  bucket = aws_s3_bucket.sbom_bucket.id
  policy = data.aws_iam_policy_document.sbom_bucket_policy.json

  depends_on = [aws_s3_bucket_public_access_block.sbom_bucket_pab]
}

# S3 bucket notification
resource "aws_s3_bucket_notification" "sbom_bucket_notification" {
  bucket = aws_s3_bucket.sbom_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.sbom_validator.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.s3_invoke]
}
