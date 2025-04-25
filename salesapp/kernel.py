import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.core_plugins import TextPlugin
from semantic_kernel.kernel import KernelArguments

load_dotenv()

kernel = Kernel()

api_key = os.environ.get('OPENAI_API_KEY')

chat_service = OpenAIChatCompletion(
    ai_model_id="gpt-4o-mini-2024-07-18",
    api_key=api_key
)
kernel.add_service(chat_service)

with open("salesapp/prompts/response_prompt.yaml", "r") as f:
    yaml_content = f.read()
        
userInteractionFunction = KernelFunctionFromPrompt.from_yaml(yaml_str=yaml_content,plugin_name="userInteractionPlugin")
kernel.add_function(plugin_name="userInteractionPlugin",function=userInteractionFunction)
