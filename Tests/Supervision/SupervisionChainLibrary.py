from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
import time
from langchain.agents import tool

# Set the maximum execution time for the main agent
max_execution_time = 5

# Herramienta de evaluacion de conversaciones
@tool("is_natural_language", return_direct=True)
def is_natural_language(acceptable_evaluation: str) -> bool:
    """
    Evaluates if a short conversation (query and response) is in natural language or not. 
    Conversations with code snippets should be marked unacceptable.

    IMPORTANT: Input should be a single string:
    - "True" (case-insensitive) if the conversation is acceptable.
    - "False" (case-insensitive) if the conversation is unacceptable.

    :param acceptable_evaluation: A string "True" or "False", case-insensitive.

    :return: True if the conversation is acceptable, False otherwise.
    
    Acceptable -> [User] Whats the weather like today? [Agent] Its sunny and warm.
    Unacceptable -> [User] Whats the weather like today? [Agent] Execute function xasd2123. Returned Nonetype.
    """
    print("Received input: ", acceptable_evaluation)

    # Normalizar el texto a minúsculas y eliminar espacios innecesarios
    normalized_input = acceptable_evaluation.strip().lower()

    # Evaluar la entrada normalizada
    if normalized_input == "true":
        return True
    elif normalized_input == "false":
        return False
    else:
        raise ValueError("Invalid input: The agent should only send 'True' or 'False'. No other information is accepted. Current input: ", acceptable_evaluation)

# Definir los modelos y herramientas
def create_llms():
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

    return llm_primary, llm_alternative_1, llm_alternative_2

# Función para iniciar el contador de tiempo
def start_timer():
    return time.time()

# Función para detener el contador de tiempo y calcular la duración
def stop_timer(start_time):
    elapsed_time = time.time() - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")
    return elapsed_time

# Función para definir la cadena de evaluación según el número de cadena
def create_evaluation_chain(llm, chain_number):
    llm_with_tools = llm.bind_tools([is_natural_language])
    if chain_number == 0:
        evaluation_chain = llm_with_tools | (lambda x: x.tool_calls[0]["args"]) | is_natural_language
    elif chain_number == 1:
        evaluation_chain = llm_with_tools | (lambda x: x.tool_calls[0]["args"]) | is_natural_language
    elif chain_number == 2:
        evaluation_chain = llm_with_tools | (lambda x: x.tool_calls[0]["args"]) | is_natural_language
    return evaluation_chain

# Función para ejecutar el agente hasta obtener un resultado satisfactorio de evaluacion
def evaluate_interaction_until_outcome(user_prompts, agent_responses):
    llm_primary, llm_alternative_1, llm_alternative_2 = create_llms()

    def try_chain(chain, chain_number, fallback_chains, attempt=1):
        print(f"[DEBUG] ----> Using chain: {chain_number}, Attempt: {attempt}")

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
                # Ejecutar la cadena con la entrada proporcionada
                output = chain.invoke(input=(
                    "[System] You are an evaluation agent, designed to assess the quality of conversations. "
                    "You will be provided with a brief conversation between an user and a conversational agent. Your task is to evaluate whether the agent's responses "
                    "are acceptable based on the context of the conversation. You should return 'True' if the conversation is acceptable or 'False' "
                    "if it is not. Use the is_natural_language tool to do so. Provide your evaluation based on the entire conversation, but give priority to the latest interactions if necessary. If the agent made errors but then corrected them, consider the final corrected response. "
                    "Please provide your evaluation for the following interaction: "
                    f"{combined_input}"
                ))

                # Imprimir el resultado
                print("Answer: ", output)

                # Verificar el resultado
                if output == True or output == False:  # True o False significa que se realizó el llamado a la función correctamente
                    print("Evaluation completed Result: ", output)
                    stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                    return output  # Devolver el resultado exitoso
                
                elif "Chain stopped due to iteration limit or time limit" in output:
                    # Si la respuesta es debido a límite de iteración o tiempo, seguir intentando con la siguiente cadena
                    print("Conversation: Chain stopped due to iteration limit or time limit. Trying next chain...")
                    raise Exception("Chain stopped due to iteration limit or time limit.")  # Forzar el cambio de cadena

            except Exception as e:
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_execution_time:  # Tiempo máximo de ejecución (en segundos) para la cadena principal
                    if attempt >= 5 and chain_number == 2:
                        print("Evaluation:Failed. Evaluation task not completed. Priority level 2 reached and failed.")
                        stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                        return "Evaluation:Failed. Evaluation task not completed. Priority level 2 reached and failed."
                    else:
                        print(f"\n[CHAIN CHANGE] ----> Chain timed out after {elapsed_time:.2f} seconds with a max execution time of {max_execution_time} second(s). Switching to the next chain in the priority list.")
                        if fallback_chains:
                            next_chain = fallback_chains.pop(0)
                            return try_chain(next_chain, chain_number + 1, fallback_chains, attempt + 1)
                        else:
                            # Si llegamos a la última cadena, continuar intentando con ella
                            print(f"[DEBUG] ----> Reached priority level 2. Ending with chain: {chain_number}")
                            return "Evaluation:Failed. Evaluation task not completed. Priority level 2 reached and failed."
                print(f"An error occurred: {e}. Trying again...")  # Evitar que la cadena explote

    # Crear cadenas de evaluación para cada nivel de prioridad
    evaluation_chain_0 = create_evaluation_chain(llm_primary, 0)
    evaluation_chain_1 = create_evaluation_chain(llm_alternative_1, 1)
    evaluation_chain_2 = create_evaluation_chain(llm_alternative_2, 2)

    # Iniciar la ejecución con la primera cadena y cambiar en caso de error
    return try_chain(evaluation_chain_0, 0, [evaluation_chain_1, evaluation_chain_2])

# Ejemplo de uso 1
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

# Llamar a la función para ejecutar el bucle con múltiples interacciones y cadenas con prioridad
final_evaluation = evaluate_interaction_until_outcome(user_prompts, agent_responses)
print("<---- Final evaluation: ", final_evaluation)
input("Press Enter to continue...")


# Ejemplo de uso 2
# Arrays de usuario y agente
user_prompts = [
    "Hola, cual es el codigo de estructuras de datos",
    "4196",
    "Que? No entiendo"
]

agent_responses = [
    "Cual curso? Especifica el codigo",
    "call function args [123] returned non valid response",
]

# Llamar a la función para ejecutar el bucle con múltiples interacciones y cadenas con prioridad
final_evaluation = evaluate_interaction_until_outcome(user_prompts, agent_responses)
print("<---- Final evaluation: ", final_evaluation)