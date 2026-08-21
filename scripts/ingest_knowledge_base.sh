#!/bin/bash

set -e

REGION="us-east-1"

KB_ID=$(cd terraform && terraform output -raw knowledge_base_id)
DATA_SOURCE_ID=$(cd terraform && terraform output -raw knowledge_base_data_source_id)

echo "Knowledge Base: $KB_ID"
echo "Data Source:    $DATA_SOURCE_ID"

echo "Starting ingestion..."

JOB_ID=$(aws bedrock-agent start-ingestion-job \
  --region "$REGION" \
  --knowledge-base-id "$KB_ID" \
  --data-source-id "$DATA_SOURCE_ID" \
  --query "ingestionJob.ingestionJobId" \
  --output text)

echo "Ingestion Job: $JOB_ID"

while true; do

  STATUS=$(aws bedrock-agent get-ingestion-job \
    --region "$REGION" \
    --knowledge-base-id "$KB_ID" \
    --data-source-id "$DATA_SOURCE_ID" \
    --ingestion-job-id "$JOB_ID" \
    --query "ingestionJob.status" \
    --output text)

  echo "Status: $STATUS"

  if [ "$STATUS" = "COMPLETE" ]; then
    echo "Ingestion completed successfully."
    break
  fi

  if [ "$STATUS" = "FAILED" ] || [ "$STATUS" = "STOPPED" ]; then
    echo "Ingestion failed."
    exit 1
  fi

  sleep 10

done