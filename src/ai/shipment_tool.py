import boto3
import os


dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)

TABLE_NAME = os.environ["SHIPMENTS_TABLE"]

table = dynamodb.Table(TABLE_NAME)


TOOL_SPEC = {
    "toolSpec": {
        "name": "get_shipment",
        "description": (
            "Retrieve live shipment information using a shipment ID. "
            "Use this tool when the customer asks about shipment status, "
            "tracking, delivery date, shipment location, or a delayed/lost shipment."
        ),
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment identifier such as SHIP-1003"
                    }
                },
                "required": [
                    "shipment_id"
                ]
            }
        }
    }
}


def get_shipment(shipment_id: str):

    response = table.get_item(
        Key={
            "shipment_id": shipment_id
        }
    )

    item = response.get("Item")

    if not item:
        return {
            "found": False,
            "shipment_id": shipment_id
        }

    return {
        "found": True,
        "shipment": item
    }