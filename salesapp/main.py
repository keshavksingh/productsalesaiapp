import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from salesapp.kernel import kernel
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.kernel import KernelArguments

app = FastAPI()

class SalesAssistantRequest(BaseModel):
    message: str


@app.on_event("startup")
async def startup_event():

    search_plugin = MCPStdioPlugin(
    name="search",
    description="Search Tools",
    command="docker",
    args=[
        "exec", "-i",
        "-e", f"COSMOS_URI={os.environ.get('COSMOS_URI')}",
        "-e", f"COSMOS_KEY={os.environ.get('COSMOS_KEY')}",
        "-e", f"COSMOS_DB={os.environ.get('COSMOS_DB')}",
        "-e", f"COSMOS_CONTAINER={os.environ.get('COSMOS_CONTAINER')}",
        "-e", f"OPENAI_API_KEY={os.environ.get('OPENAI_API_KEY')}",
        "mcpserver",
        "python", "/mcp/mcpserver/mcp_server.py"])
    
    print("Connecting to MCP Plugin...")
    await MCPStdioPlugin.connect(search_plugin)
    print("MCP Plugin connected.")
    await search_plugin.__aenter__()

    kernel.add_plugin(search_plugin, plugin_name="search")
    print(f"Plugins loaded: {kernel.plugins.keys()}")
    for plugin in kernel.plugins.keys():
        function_names = list(kernel.plugins[plugin].functions.keys())
        print(f"Plugin '{plugin}' Plugin functions: {function_names}")


@app.post("/salesassistant")
async def chat_endpoint(request: SalesAssistantRequest):
    user_input = request.message
    if not user_input:
        return {"error": "Missing message"}
    
    result = await kernel.invoke(
                plugin_name="search",
                function_name="search_products",
                query=user_input
                )
    response_json = str(result)
    print(f"Result:\n{response_json}")

    extraction_args = KernelArguments(input= user_input, search_context = response_json)

    final_response = await kernel.invoke(
        plugin_name="userInteractionPlugin",
        function_name="userInteractionFunction",
        arguments=extraction_args
    )

    print(f"Final response: {final_response}")
    return {"response": str(final_response)}
