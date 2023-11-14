terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region     = "us-east-2"
#  access_key = "AKIAQN6TTLSWRLRV353P"
#  secret_key = "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"
}

