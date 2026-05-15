terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket       = "security.state.example.com"
    key          = "terraform/device-sbom-audit/terraform-state-file.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"

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

