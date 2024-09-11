from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_groq import ChatGroq
import os
import time

# Importar librería propia
from TaggingToolsLibrary import *

# Set the maximum execution time for the main agent
max_execution_time = 5

# Definir los modelos y agentes
def create_agents():
    # Definir el modelo principal (Llama)
    llm_primary = ChatOpenAI(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    # Definir el modelo alternativo 1 (Groq)
    llm_alternative_1 = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
    )

    # Definir el modelo alternativo 2 (otro modelo, por ejemplo)
    llm_alternative_2 = ChatOpenAI(
        model="openai/gpt-3.5-turbo",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        base_url="https://api.openai.com/v1",
        api_key="openai-api-key"
    )

    # Inicializar los agentes
    agent_primary = initialize_agent(
        [multiple_input_tag_interaction], 
        llm_primary,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time  # Tiempo máximo de ejecución (en segundos) para el agente principal
    )

    agent_alternative_1 = initialize_agent(
        [multiple_input_tag_interaction], 
        llm_alternative_1,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time  # Tiempo máximo de ejecución (en segundos) para el agente secundario
    )

    agent_alternative_2 = initialize_agent(
        [multiple_input_tag_interaction], 
        llm_alternative_2,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
        verbose=True
    )

    return [agent_primary, agent_alternative_1, agent_alternative_2]

# Función para iniciar el contador de tiempo
def start_timer():
    return time.time()

# Función para detener el contador de tiempo y calcular la duración
def stop_timer(start_time):
    elapsed_time = time.time() - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")
    return elapsed_time

# Función para ejecutar el agente hasta obtener un resultado satisfactorio de tagging
def tag_interaction_until_ok(user_prompts, agent_responses):
    agents_with_priority = create_agents()
    
    def try_agent(agent, agent_number, fallback_agents, attempt=1):
        print(f"[DEBUG] ----> Using agent: {agent_number}, Attempt: {attempt}")

        interactions = []
        max_len = max(len(user_prompts), len(agent_responses))
        
        for i in range(max_len):
            if i < len(user_prompts):
                interactions.append(f"[User] {user_prompts[i]}")
            if i < len(agent_responses):
                interactions.append(f"[Agent] {agent_responses[i]}")
        
        # Unimos todas las interacciones en una sola entrada de texto
        combined_input = " ".join(interactions)
        print("[DEBUG] ----> Final input: ", combined_input)
        
        start_time = start_timer()  # Iniciar el contador de tiempo
        
        while True:
            try:
                # Ejecutar el agente con la entrada proporcionada
                output = agent.run(
                    input=(
                        "[System] You are an interaction tagger agent, designed to tag interactions based on sentiment. "
                        "You will be given a series of user prompts and agent responses. Your task is to use the multiple_input_tag_interaction tool "
                        "to tag the sentiment of each agent response as either positive (pos) or negative (neg) and the language in which the "
                        "user prompt and agent response are written, like 'en' for English or 'es' for Spanish. You can summarize the interaction, but always give priority to the latest ones."
                        "if necessary. Please provide the appropriate tag for the following interaction: "
                        f"{combined_input}"
                    )
                )

                # Imprimir el resultado
                print("Answer: ", output)

                # Verificar si el resultado comienza con "Tag:Done"
                if output.startswith("Tag:Done"):  # Tag:Done. Significa que se realizó el llamado a la función correctamente
                    print("Tagging complete and successful.")
                    stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                    return output  # Devolver el resultado exitoso
                
                elif "Agent stopped due to iteration limit or time limit" in output:
                    # Si la respuesta es debido a límite de iteración o tiempo, seguir intentando con el siguiente agente
                    print("Conversation: Agent stopped due to iteration limit or time limit. Trying next agent...")
                    raise Exception("Agent stopped due to iteration limit or time limit.")  # Forzar el cambio de agente

            except Exception as e:
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_execution_time:  # Tiempo máximo de ejecución (en segundos) para el agente principal
                    if attempt >= 5 and agent_number == 2:
                        print("Tag:Failed. Tagging task not completed. Priority level 2 reached and failed.")
                        stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                        return "Tag:Failed. Tagging task not completed. Priority level 2 reached and failed."
                    else:
                        print(f"\n[AGENT CHANGE] ----> Agent timed out after {elapsed_time:.2f} seconds with a max execution time of {max_execution_time} second(s). Switching to the next agent in the priority list.")
                        if fallback_agents:
                            next_agent = fallback_agents.pop(0)
                            return try_agent(next_agent, agent_number + 1, fallback_agents, attempt + 1)
                        else:
                            # Si llegamos al último agente, continuar intentando con él
                            print(f"[DEBUG] ----> Reached priority level 2. Ending with agent: {agent_number}")
                            return "Tag:Failed. Tagging task not completed. Priority level 2 reached and failed."
                print(f"An error occurred: {e}. Trying again...")  # Evitar que el agente explote

    # Iniciar la ejecución con el primer agente y cambiar en caso de error
    return try_agent(agents_with_priority.pop(0), 0, agents_with_priority)

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

# Llamar a la función para ejecutar el bucle con múltiples interacciones y agentes con prioridad
final_tag = tag_interaction_until_ok(user_prompts, agent_responses)
print("<---- Final tag: ", final_tag)
