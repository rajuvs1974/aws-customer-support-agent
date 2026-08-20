resource "aws_dynamodb_table" "customers" {
  name         = "${var.project_name}-${var.environment}-customers"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "customer_id"

  attribute {
    name = "customer_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "orders" {
  name         = "${var.project_name}-${var.environment}-orders"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "shipments" {
  name         = "${var.project_name}-${var.environment}-shipments"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "shipment_id"

  attribute {
    name = "shipment_id"
    type = "S"
  }
}