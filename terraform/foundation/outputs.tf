output "knowledge_bucket_name" {
  description = "Persistent S3 knowledge bucket"
  value       = aws_s3_bucket.knowledge_documents.bucket
}

output "shipments_table" {
  description = "Persistent shipment DynamoDB table"
  value       = aws_dynamodb_table.shipments.name
}

output "customers_table" {
  value = aws_dynamodb_table.customers.name
}

output "orders_table" {
  value = aws_dynamodb_table.orders.name
}