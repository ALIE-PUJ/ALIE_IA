from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import tool
from datetime import date

# Definir el modelo
llm = ChatOpenAI(
    model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    temperature=0.9,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"    # organization="...",
    # other params...
)

# Q&A
question = "How are you?"

result = llm.invoke(question) 
print("Answer: ", result)

# Si se queda en un bucle de "Pensamiento" hay que hacer manejo de errores