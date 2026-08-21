output "api_url" {
  description = "Customer support API URL"
  value       = aws_apigatewayv2_stage.default.invoke_url
}