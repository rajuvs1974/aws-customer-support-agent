#!/bin/bash

set -e

BUCKET_NAME=$(cd terraform && terraform output -raw knowledge_bucket_name)

echo "Uploading policy documents to:"
echo "s3://$BUCKET_NAME/policies/"

aws s3 sync \
  data/policies/ \
  "s3://$BUCKET_NAME/policies/" \
  --delete

echo "Documents synchronized successfully."