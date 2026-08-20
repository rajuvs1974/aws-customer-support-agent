import boto3
import os


bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)

KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]


def retrieve_context(query: str, number_of_results: int = 5):

    response = bedrock_agent.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": number_of_results
            }
        },
        retrievalQuery={
            "text": query
        }
    )

    results = response.get("retrievalResults", [])

    context = []
    sources = []

    # Conservative threshold for the initial demo.
    # We will tune this later using an evaluation dataset.
    MIN_RELEVANCE_SCORE = 0.50

    for result in results:

        score = result.get("score", 0)

        if score < MIN_RELEVANCE_SCORE:
            continue

        text = result.get("content", {}).get("text", "")

        location = result.get("location", {})

        s3_location = location.get("s3Location", {})

        uri = s3_location.get("uri")

        if text:
            context.append(text)

        if uri:
            sources.append(uri)

    return context, list(dict.fromkeys(sources))