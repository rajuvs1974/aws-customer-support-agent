resource "aws_s3vectors_vector_bucket" "knowledge" {
  vector_bucket_name = "${var.project_name}-${var.environment}-vectors"
  lifecycle {
    ignore_changes = [
      force_destroy
    ]
  }
}
resource "aws_s3vectors_index" "knowledge" {
  vector_bucket_name = aws_s3vectors_vector_bucket.knowledge.vector_bucket_name

  index_name = "${var.project_name}-${var.environment}-index"

  data_type = "float32"

  dimension = 1024

  distance_metric = "cosine"

  metadata_configuration {
    non_filterable_metadata_keys = [
      "AMAZON_BEDROCK_TEXT",
      "AMAZON_BEDROCK_METADATA"
    ]
  }
}