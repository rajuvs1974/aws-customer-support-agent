variable "aws_region" {
  description = "AWS region for the project"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "customer-support-agent"
}
variable "bedrock_model_id" {
  description = "Amazon Bedrock foundation model ID"
  type        = string
  default     = "amazon.nova-lite-v1:0"
}
