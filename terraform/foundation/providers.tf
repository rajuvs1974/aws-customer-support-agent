provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "aws-customer-support-agent"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Portfolio   = "AI-Engineering"
    }
  }
}