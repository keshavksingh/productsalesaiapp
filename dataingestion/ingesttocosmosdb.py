import os
import json
from pathlib import Path
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import uuid

load_dotenv()

COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = os.getenv("COSMOS_DB")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER")

client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
database = client.get_database_client(COSMOS_DB)
container = database.get_container_client(COSMOS_CONTAINER)

# Directory containing product JSON files
data_dir = Path("product_data")

if not data_dir.exists():
    raise FileNotFoundError(f"Directory {data_dir} does not exist.")

# Ingest documents
for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
        with open(os.path.join(data_dir, filename), "r") as file:
            document = json.load(file)
            try:
                document["id"] = str(uuid.uuid4())
                container.upsert_item(document)
                print(f"Ingested: {filename}")
            except Exception as e:
                print(f"Failed to ingest {filename}: {e}")
