output "knowledge_bucket_name" {
  description = "S3 bucket containing customer support knowledge"
  value       = aws_s3_bucket.knowledge_documents.bucket
}

output "customers_table" {
  value = aws_dynamodb_table.customers.name
}

output "orders_table" {
  value = aws_dynamodb_table.orders.name
}

output "shipments_table" {
  value = aws_dynamodb_table.shipments.name
}
output "api_url" {
  description = "Customer support API URL"
  value       = aws_apigatewayv2_stage.default.invoke_url
}