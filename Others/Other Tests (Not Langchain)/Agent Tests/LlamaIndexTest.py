from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.lmstudio import LMStudio
from llama_index.core.base.llms.types import ChatMessage, MessageRole

# pip install llama-index-llms-lmstudio

# Definir el modelo con la libreria propia de llamaindex
llm = LMStudio( 
    model_name="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    base_url="http://localhost:1234/v1",
    temperature=0.9,
    api_key="lm-studio"    # organization="...",
    # other params...
)


def get_weather(location: str) -> str:
    """Usfeful for getting the weather for a given location."""
    ...

tool = FunctionTool.from_defaults(
    get_weather,
    # async_fn=aget_weather,  # optional!
)

tools = [tool]

agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)
response = agent.chat("Who are you?")
print(response)