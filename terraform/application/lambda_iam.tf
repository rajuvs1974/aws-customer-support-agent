resource "aws_iam_role" "ai_lambda_role" {
  name = "${var.project_name}-${var.environment}-ai-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.ai_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
resource "aws_iam_role_policy" "bedrock_invoke" {
  name = "${var.project_name}-${var.environment}-bedrock-invoke"

  role = aws_iam_role.ai_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel"
        ]

        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_role_policy" "lambda_knowledge_base" {
  name = "${var.project_name}-${var.environment}-lambda-kb"
  role = aws_iam_role.ai_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "bedrock:Retrieve"
        ]

        Resource = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/${data.terraform_remote_state.foundation.outputs.knowledge_base_id}"
      }
    ]
  })
}
resource "aws_iam_role_policy" "lambda_shipment_lookup" {
  name = "${var.project_name}-${var.environment}-shipment-lookup"
  role = aws_iam_role.ai_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "dynamodb:GetItem"
        ]

        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${data.terraform_remote_state.foundation.outputs.shipments_table}"
      }
    ]
  })
}