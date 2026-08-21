import json
import boto3
import os

from rag import retrieve_context
from prompts import SYSTEM_PROMPT
from shipment_tool import get_shipment, TOOL_SPEC


bedrock = boto3.client(
    "bedrock-runtime",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)

MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0"
)

def clean_answer(text: str) -> str:
    if "<thinking>" in text and "</thinking>" in text:
        start = text.find("<thinking>")
        end = text.find("</thinking>") + len("</thinking>")

        text = text[:start] + text[end:]

    return text.strip()
def lambda_handler(event, context):

    try:
        # ---------------------------------------------------------
        # Parse request
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Retrieve relevant policy context
        # ---------------------------------------------------------

        retrieved_context, sources = retrieve_context(message)

        context_text = ""

        if retrieved_context:
            context_text = "\n\n---\n\n".join(
                retrieved_context
            )

        else:
            context_text = (
                "No relevant company policy information was found."
            )

        # ---------------------------------------------------------
        # Build prompt
        # ---------------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

COMPANY POLICY CONTEXT:

{context_text}

CUSTOMER QUESTION:

{message}

You have access to a tool called get_shipment.

Use get_shipment when the customer asks about a specific shipment,
tracking status, delivery status, estimated delivery date,
shipment location, delayed shipment, or lost shipment.

Use the company policy context when answering policy questions.

If the customer asks about a shipment, use the tool to retrieve
the live shipment information before answering.

Do not invent shipment information.

If the shipment cannot be found, clearly tell the customer that
the shipment could not be found.

If the available company policies do not contain enough information
to answer a policy question, say:

"I don't have enough information in the available company policies
to answer that question."

Provide a concise and professional answer.
"""

        # ---------------------------------------------------------
        # First model call
        # ---------------------------------------------------------

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

            "toolConfig": {
                "tools": [
                    TOOL_SPEC
                ]
            },

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

        output_message = response_body["output"]["message"]

        content = output_message.get("content", [])

        # ---------------------------------------------------------
        # Check whether Nova requested a tool
        # ---------------------------------------------------------

        tool_use = None

        for item in content:

            if "toolUse" in item:
                tool_use = item["toolUse"]
                break

        # ---------------------------------------------------------
        # Tool execution
        # ---------------------------------------------------------

        if tool_use:

            tool_name = tool_use["name"]
            tool_input = tool_use["input"]
            tool_use_id = tool_use["toolUseId"]

            if tool_name == "get_shipment":

                shipment_id = tool_input.get("shipment_id")

                if not shipment_id:

                    return response(
                        400,
                        {
                            "error": (
                                "Shipment ID was not provided "
                                "by the model."
                            )
                        }
                    )

                # Call DynamoDB tool
                tool_result = get_shipment(
                    shipment_id
                )

                # -------------------------------------------------
                # Send tool result back to Nova
                # -------------------------------------------------

                tool_message = {
                    "role": "user",
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [
                                    {
                                        "json": tool_result
                                    }
                                ]
                            }
                        }
                    ]
                }

                # Add assistant tool request
                request_body["messages"].append(
                    output_message
                )

                # Add tool result
                request_body["messages"].append(
                    tool_message
                )

                # -------------------------------------------------
                # Second model call
                # -------------------------------------------------

                second_response = bedrock.invoke_model(
                    modelId=MODEL_ID,
                    body=json.dumps(request_body)
                )

                second_response_body = json.loads(
                    second_response["body"].read()
                )

                final_message = (
                    second_response_body["output"]["message"]
                )

                final_content = final_message.get(
                    "content",
                    []
                )

                answer = ""

                for item in final_content:

                    if "text" in item:
                        answer = clean_answer(item["text"])
                        break

                if not answer:
                    answer = (
                        "I was able to retrieve the shipment "
                        "information, but I could not generate "
                        "a response."
                    )

                return response(
                    200,
                    {
                        "response": answer,
                        "sources": sources,
                        "tool_used": "get_shipment",
                        "shipment_id": shipment_id
                    }
                )

        # ---------------------------------------------------------
        # Normal RAG response — no tool required
        # ---------------------------------------------------------

        answer = ""

        for item in content:

            if "text" in item:
                answer = clean_answer(item["text"])
                break

        if not answer:

            answer = (
                "I don't have enough information in the "
                "available company policies to answer that question."
            )

        return response(
            200,
            {
                "response": answer,
                "sources": sources,
                "tool_used": None
            }
        )

    # -------------------------------------------------------------
    # Error handling
    # -------------------------------------------------------------

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


# -----------------------------------------------------------------
# API response helper
# -----------------------------------------------------------------

def response(status_code, body):

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }