import json
import boto3
import os

from rag import retrieve_context
from prompts import SYSTEM_PROMPT


bedrock = boto3.client(
    "bedrock-runtime",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)

MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0"
)


def lambda_handler(event, context):

    try:

        body = event

        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])

        message = body.get("message")

        if not message:
            return response(
                400,
                {
                    "error": "message is required"
                }
            )

        # Retrieve relevant policy context
        retrieved_context, sources = retrieve_context(message)

        if not retrieved_context:
            return response(
                200,
                {
                    "response": (
                        "I don't have enough information in the "
                        "available company policies to answer that question."
                    ),
                    "sources": []
                }
            )

        context_text = "\n\n---\n\n".join(retrieved_context)

        prompt = f"""
{SYSTEM_PROMPT}

COMPANY POLICY CONTEXT:

{context_text}

CUSTOMER QUESTION:

{message}

Provide the best answer using only the company policy context.
"""

        request_body = {
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.1
            }
        }

        bedrock_response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )

        response_body = json.loads(
            bedrock_response["body"].read()
        )

        answer = (
            response_body["output"]
            ["message"]
            ["content"][0]
            ["text"]
        )

        return response(
            200,
            {
                "response": answer,
                "sources": sources
            }
        )

    except Exception as exc:

        print(
            json.dumps(
                {
                    "error": str(exc)
                }
            )
        )

        return response(
            500,
            {
                "error": "Internal server error"
            }
        )


def response(status_code, body):

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }