resource "aws_iam_role" "bedrock_kb_role" {
  name = "${var.project_name}-${var.environment}-bedrock-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "bedrock.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy" "bedrock_kb_s3" {
  name = "${var.project_name}-${var.environment}-bedrock-kb-s3"
  role = aws_iam_role.bedrock_kb_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]

        Resource = [
          aws_s3_bucket.knowledge_documents.arn,
          "${aws_s3_bucket.knowledge_documents.arn}/*"
        ]
      }
    ]
  })
}
resource "aws_iam_role_policy" "bedrock_kb_embedding" {
  name = "${var.project_name}-${var.environment}-bedrock-kb-embedding"
  role = aws_iam_role.bedrock_kb_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel"
        ]

        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
      }
    ]
  })
}
resource "aws_iam_role_policy" "bedrock_kb_vectors" {
  name = "${var.project_name}-${var.environment}-bedrock-kb-vectors"
  role = aws_iam_role.bedrock_kb_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3vectors:GetIndex",
          "s3vectors:QueryVectors",
          "s3vectors:PutVectors",
          "s3vectors:GetVectors",
          "s3vectors:DeleteVectors"
        ]

        Resource = aws_s3vectors_index.knowledge.index_arn
      }
    ]
  })
}