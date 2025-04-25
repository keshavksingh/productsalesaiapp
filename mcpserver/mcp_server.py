import os
import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from azure.cosmos import CosmosClient
from fastapi_mcp import FastApiMCP
from mcp.server.fastmcp import FastMCP

load_dotenv()

COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = os.getenv("COSMOS_DB")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

mcp = FastMCP("search")
faiss_index = None
product_metadata = []

def embed_text(text):
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
    return response

def initialize_vector_index():
    global faiss_index, product_metadata
    client = CosmosClient(COSMOS_URI, COSMOS_KEY)
    container = client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

    documents = list(container.read_all_items())
    vectors = []
    metadata = []

    for doc in documents:
        text = f"Product: {doc['productname']}\nDescription: {doc['productdescription']}\nPrice: ${doc['productprice']}\nWarranty: {doc['productwarrantyinmonths']} months"
        try:
            embedding = embed_text(text)
            vectors.append(embedding)
            metadata.append({
                "productid": doc["productid"],
                "productname": doc["productname"],
                "productdescription": doc["productdescription"],
                "productprice": doc["productprice"],
                "productwarrantyinmonths": doc["productwarrantyinmonths"]
            })
        except Exception as e:
            print(f"Failed to embed {doc['productid']}: {e}")

    if not vectors:
        raise ValueError("No embeddings generated")

    vector_array = np.array(vectors).astype('float32')
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vector_array)

    faiss_index = index
    product_metadata = metadata
    print("FAISS index initialized with", len(metadata), "documents.")

@mcp.tool(name="search_products", description="Search relevant product details.")
async def search_products(query: str = Query(..., min_length=5)):
    if faiss_index is None:
        raise HTTPException(status_code=500, detail="FAISS index not initialized")

    query_embedding = embed_text(query)
    D, I = faiss_index.search(np.array([query_embedding]).astype('float32'), k=5)

    results = []
    for idx in I[0]:
        if idx < len(product_metadata):
            results.append(product_metadata[idx])

    return {"results": results}


if __name__ == "__main__":
    print("Initializing Search MCP Server...")
    initialize_vector_index()
    print("Starting MCP server with Search tools...")
    mcp.run(transport='stdio')