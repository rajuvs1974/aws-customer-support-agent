resource "aws_apigatewayv2_api" "customer_support" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_integration" "ai_lambda" {
  api_id = aws_apigatewayv2_api.customer_support.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.ai.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "chat" {
  api_id    = aws_apigatewayv2_api.customer_support.id
  route_key = "POST /chat"
  target    = "integrations/${aws_apigatewayv2_integration.ai_lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.customer_support.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.customer_support.execution_arn}/*/*"
}