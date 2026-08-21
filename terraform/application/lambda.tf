data "archive_file" "ai_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/ai"
  output_path = "${path.module}/../../src/ai/invoke_model.zip"
}

resource "aws_lambda_function" "ai" {
  function_name = "${var.project_name}-${var.environment}-ai"

  filename         = data.archive_file.ai_lambda.output_path
  source_code_hash = data.archive_file.ai_lambda.output_base64sha256

  role = aws_iam_role.ai_lambda_role.arn

  handler = "invoke_model.lambda_handler"
  runtime = "python3.12"

  timeout     = 30
  memory_size = 512

  environment {
    variables = {
      BEDROCK_MODEL_ID  = var.bedrock_model_id
      KNOWLEDGE_BASE_ID = data.terraform_remote_state.foundation.outputs.knowledge_base_id
      SHIPMENTS_TABLE   = data.terraform_remote_state.foundation.outputs.shipments_table
    }
  }

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash,
      publish
    ]
  }
}