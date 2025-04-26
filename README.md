# Sales Assistant AI App
 This is a demonstration of a Retrieval Augmented Generation over a LLM GenAI solution. The example showcases product sales ai assistant capable of answering questions on products based on vector search (over FAISS) for context data and a prompt engineering plugin to answer customers with queries on product details. Intially we load the data from Azure Cosmos DB, generate its embedding and index and data on product details into **FAISS (In-Memory)**. This is loaded into a MCP Server serving **"search product"** as a plugin. This is containerized as **MCPSERVER**. 
 We build another container as FastAPI APP serving API for the end customers. For all queries from customers we perform (a) & (b) by calling the MCP Server and (c) on the FastAPI Server with Microsoft's Semantic Kernel SDK **a.) we generate embeddings through OpenAI model="text-embedding-3-small" b.) we then search semantic similarity and get top 5 documents against the query and generate the search context data. c.) Finally we feed the initial query and search context into the userInteractionFunction part of userInteractionPlugin to craft the response to the customer on the query.**

 This typically demonstrates a clean semantic RAG implementation with everything under the hood.

![image](https://github.com/user-attachments/assets/81ed0603-ccae-4478-b9b1-3e4ce55cf7c9)

Video Demonstration - https://youtu.be/urWO7pmwces
