terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state with locking. Fill in real values per account; the state bucket is created once, outside this code.
  backend "s3" {
    bucket         = "novapay-tfstate-REPLACE_ME"
    key            = "platform/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "novapay-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "novapay-cicd"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
