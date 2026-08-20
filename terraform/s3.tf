
resource "aws_s3_bucket" "knowledge_documents" {
  bucket = "${var.project_name}-${var.environment}-knowledge"

  force_destroy = true
}

resource "aws_s3_bucket_versioning" "knowledge_documents" {
  bucket = aws_s3_bucket.knowledge_documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "knowledge_documents" {
  bucket = aws_s3_bucket.knowledge_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}