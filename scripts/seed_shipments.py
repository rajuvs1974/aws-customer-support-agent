import json
import boto3
import subprocess
from pathlib import Path


REGION = "us-east-1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TERRAFORM_DIR = PROJECT_ROOT / "terraform"
DATA_FILE = PROJECT_ROOT / "data" / "shipments.json"


result = subprocess.run(
    [
        "terraform",
        "-chdir=" + str(TERRAFORM_DIR),
        "output",
        "-raw",
        "shipments_table",
    ],
    capture_output=True,
    text=True,
    check=True,
)

table_name = result.stdout.strip()

dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION,
)

table = dynamodb.Table(table_name)

with open(DATA_FILE, "r") as file:
    shipments = json.load(file)

with table.batch_writer() as batch:
    for shipment in shipments:
        batch.put_item(Item=shipment)

print(f"Inserted {len(shipments)} shipments into {table_name}")