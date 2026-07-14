terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.45"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.3"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.8"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      app        = "device-sbom-audit"
      managed_by = "terraform"
    }
  }
}

# Data source for current AWS account and region
data "aws_caller_identity" "current" {}

locals {
  lambda_function_name = "device-sbom-audit"
}

