from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_groq import ChatGroq
import os
import time
from langchain.agents import tool

# Herramienta de evaluacion de conversaciones
@tool("interaction_evaluator", return_direct=True)
def interaction_evaluator(acceptable_evaluation: str) -> bool:
    """
    This tool evaluates whether a short piece of a conversation (typically a query and its response) is acceptable or not.
    An acceptable conversation is defined as one with a natural language outcome. Conversations that are incomplete, or 
    that include code snippets, technical details, or other non-natural language content should be marked as unacceptable.

    IMPORTANT: This tool only expects a single string input from the agent:
    - "True" (case-insensitive) if the conversation is acceptable.
    - "False" (case-insensitive) if the conversation is unacceptable.

    The input should NOT include the entire conversation or any other information. It should be a simple "True" or "False" string only.

    :param acceptable_evaluation: A single string provided by the agent, either "True" or "False". 
                        This input is case-insensitive and will be normalized to handle variations like "true", "TRUE", etc.

    :return: A boolean value:
             - True if the conversation is deemed acceptable by the agent.
             - False if the conversation is deemed unacceptable by the agent.
    
    :raises ValueError: If the input is anything other than "True" or "False".
    """

    # Normalizar el texto a minúsculas y eliminar espacios innecesarios
    normalized_input = acceptable_evaluation.strip().lower()

    # Evaluar la entrada normalizada
    if normalized_input == "true":
        return True
    elif normalized_input == "false":
        return False
    else:
        raise ValueError("Invalid input: The agent should only send 'True' or 'False'. No other information is accepted. Current input: ", acceptable_evaluation)


# Set the maximum execution time for the main agent
max_execution_time = 10

# Definir los modelos y agentes
def create_llms():
    # Definir el modelo principal (Llama)
    llm_primary = ChatOpenAI(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        tool_choice="interaction_evaluator"
    )
    llm_primary = llm_primary.bind_tools([interaction_evaluator])

    # Definir el modelo alternativo 1 (Groq)
    llm_alternative_1 = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        tool_choice="interaction_evaluator"
    )
    llm_alternative_1 = llm_alternative_1.bind_tools([interaction_evaluator])

    # Definir el modelo alternativo 2 (otro modelo, por ejemplo)
    llm_alternative_2 = ChatOpenAI(
        model="openai/gpt-3.5-turbo",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        base_url="https://api.openai.com/v1",
        api_key="openai-api-key",
        tool_choice="interaction_evaluator"
    )
    llm_alternative_2 = llm_alternative_2.bind_tools([interaction_evaluator])

    return [llm_primary, llm_alternative_1, llm_alternative_2]

# Función para iniciar el contador de tiempo
def start_timer():
    return time.time()

# Función para detener el contador de tiempo y calcular la duración
def stop_timer(start_time):
    elapsed_time = time.time() - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")
    return elapsed_time

# Ejemplo de uso
# Arrays de usuario y agente
user_prompts = [
    "Hola, cual es el codigo de estructuras de datos",
    "4196",
    "Perfecto, gracias!"
]

agent_responses = [
    "Cual curso? Especifica el codigo",
    "El curso de estructuras de datos es 4196"
]

# Crear la interaccion como un string
interactions = []
max_len = max(len(user_prompts), len(agent_responses))
        
for i in range(max_len):
    if i < len(user_prompts):
        interactions.append(f"[User] {user_prompts[i]}")
    if i < len(agent_responses):
        interactions.append(f"[Agent] {agent_responses[i]}")
        
# Unimos todas las interacciones en una sola entrada de texto
conversation = " ".join(interactions)
print("[DEBUG] ----> Final input: ", conversation)


# LLM definition

# Groq
llm_primary = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.9,
    max_tokens=None,
    timeout=None
)

# LM Studio
'''
llm_primary = ChatOpenAI(
    model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    temperature=0.9,
    max_tokens=None,
    timeout=None,
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    tool_choice="interaction_evaluator"
)
'''

# MATH EXAMPLE
'''
print("\nMATH EXAMPLE")

@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

print("Tool invocation result: ", multiply.invoke({"first_int": 4, "second_int": 5}))

llm_primary_with_tools = llm_primary.bind_tools([multiply])

from operator import itemgetter

chain = llm_primary_with_tools | (lambda x: x.tool_calls[0]["args"]) | multiply

msg = llm_primary_with_tools.invoke("whats 5 times forty two")
print("Tool invocation call:", msg.tool_calls)

# Llamar a la función para ejecutar el bucle con múltiples interacciones y agentes con prioridad
final_evaluation = chain.invoke("whats 5 times forty two")
print("<---- Final Evaluation: ", final_evaluation)
#input("Press Enter to continue...")
'''



# EVALUATION
print("\nEVALUATION EXAMPLE")

print("Tool invocation result: ", interaction_evaluator.invoke({"acceptable_evaluation": "True"}))

llm_primary_with_tools = llm_primary.bind_tools([interaction_evaluator])

from operator import itemgetter

evaluation_chain = llm_primary_with_tools | (lambda x: x.tool_calls[0]["args"]) | interaction_evaluator

msg = llm_primary_with_tools.invoke(conversation)
print("Tool invocation call:", msg.tool_calls)

# Evaluar una conversacion correcta
final_evaluation = evaluation_chain.invoke(conversation)
print("\n<---- Interaction: ", conversation)
print("<---- Final Evaluation: ", final_evaluation)

# Evaluar una conversacion incorrecta
incorrect_conversation = "[User] Hola, cual es el codigo de estructuras de datos [Agent] exception: invalid input"
final_evaluation = evaluation_chain.invoke(incorrect_conversation)
print("\n<---- Interaction: ", incorrect_conversation)
print("<---- Final Evaluation: ", final_evaluation)


# Nota: Las cadenas NO FUNCIONAN bien con LLMs Locales.