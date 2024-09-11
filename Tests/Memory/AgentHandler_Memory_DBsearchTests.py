from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from datetime import date
import os
import time
from langchain.agents import tool

# Importar librería propia
from Library.DBsearchTests_Library import *

# Set the maximum execution time for the main agent
max_execution_time = 2

# Herramienta general
@tool
def general_query_handler(user_input: str) -> str:
    """
    Handle general queries directed to the conversational agent ALIE.

    This function is designed to respond to common user queries that do not require specific
    information from databases or external tools. It includes responses to questions about
    the agent's identity, purpose, and general academic inquiries.

    Parameters:
    user_input (str): The input query from the user.

    Returns:
    str: The response generated by ALIE for the given input.
    """
    
    # Normalize user input to lowercase for easier matching
    normalized_input = user_input.lower()

    # Define standard responses for general queries
    responses = {
        "who are you": "I am ALIE, an academic assistance agent designed to help resolve inquiries at Javeriana University.",
        "what is your name": "My name is ALIE, which stands for Academic Learning and Information Expert.",
        "what do you do": "I assist with academic inquiries and provide support for students, faculty, and staff at Javeriana University.",
        "how can you help me": "I can help you with a variety of academic-related questions, such as course information, schedules, and general university resources.",
        "tell me about yourself": "I am ALIE, a conversational agent developed to enhance the academic experience at Javeriana University by providing timely and accurate information.",
        "what is javeriana university": "Javeriana University, also known as Pontificia Universidad Javeriana, is a prestigious educational institution located in Colombia, known for its excellence in teaching and research.",
        "what services do you offer": "I offer support in resolving academic inquiries, providing information about courses, schedules, and other university-related matters."
    }

    # Default response if the query doesn't match any predefined general queries
    default_response = "I'm here to help with any academic inquiries you may have. How can I assist you today?"

    # Check if the user input matches any predefined queries
    response = responses.get(normalized_input, default_response)

    return response

# Definir los modelos
def create_agents():
    # Definir el modelo principal (Llama)
    llm_primary = ChatOpenAI(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        temperature=0.9,
        max_tokens=None,
        timeout=None,
        max_retries=2,
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
        [general_query_handler,
         get_students_by_name,
         get_course_by_name,
         get_classes_by_course_code,
         get_classes_by_course_name,
         get_class_by_code,
         get_prerequisites_by_course_code,
         get_prerequisites_by_course_name,
         get_class_schedule,
         get_teacher_by_name], 
        llm_primary,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time
    )

    agent_alternative_1 = initialize_agent(
        [general_query_handler,
         get_students_by_name,
         get_course_by_name,
         get_classes_by_course_code,
         get_classes_by_course_name,
         get_class_by_code,
         get_prerequisites_by_course_code,
         get_prerequisites_by_course_name,
         get_class_schedule,
         get_teacher_by_name], 
        llm_alternative_1,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time
    )

    agent_alternative_2 = initialize_agent(
        [general_query_handler,
         get_students_by_name,
         get_course_by_name,
         get_classes_by_course_code,
         get_classes_by_course_name,
         get_class_by_code,
         get_prerequisites_by_course_code,
         get_prerequisites_by_course_name,
         get_class_schedule,
         get_teacher_by_name], 
        llm_alternative_2,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
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

# Función para ejecutar el agente hasta obtener un resultado satisfactorio de Conversation
def execute_agent_until_success(question):
    agents_with_priority = create_agents()
    
    def try_agent(agent, agent_number, fallback_agents, attempt=1):
        print(f"[DEBUG] ----> Using agent: {agent_number}, Attempt: {attempt}")

        start_time = start_timer()  # Iniciar el contador de tiempo
        
        while True:
            try:
                # Ejecutar el agente con la pregunta proporcionada
                output = agent.run(
                    input=(
                        "[System] You are ALIE, an academic assistance agent designed to help resolve inquiries at Javeriana University. Use tools to retrieve information from databases and external sources, or just answer without the use of tools if the user just wants to interact with you. Answer as quick as possible, but with high quality and as much detail as needed."
                        " [User] " + question
                    )
                )

                # Imprimir el resultado
                print("Answer: ", output)

                # Verificar si el resultado es exitoso
                if "Error:" not in output and "Agent stopped due to iteration limit or time limit" not in output:
                    print("Conversation complete and successful.")
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
                        print("Conversation:Failed. Conversation task not completed. Priority level 2 reached and failed.")
                        stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                        return "Conversation:Failed. Conversation task not completed. Priority level 2 reached and failed."
                    else:
                        print(f"\n[AGENT CHANGE] ----> Agent timed out after {elapsed_time:.2f} seconds with a max execution time of {max_execution_time} second(s). Switching to the next agent in the priority list.")
                        if fallback_agents:
                            next_agent = fallback_agents.pop(0)
                            return try_agent(next_agent, agent_number + 1, fallback_agents, attempt + 1)
                        else:
                            # Si llegamos al último agente, continuar intentando con él
                            print(f"[DEBUG] ----> Reached priority level 2. Ending with agent: {agent_number}")
                            stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                            return "Conversation:Failed. Conversation task not completed. Priority level 2 reached and failed."
                print(f"An error occurred: {e}. Trying again...")  # Evitar que el agente explote

    # Iniciar la ejecución con el primer agente y cambiar en caso de error
    return try_agent(agents_with_priority.pop(0), 0, agents_with_priority)

# Ejemplo de uso
questions = [
    "Is there any student called Luis? Who?",
    "Which is the course code for Estructuras de datos?",
    "Which are the available classes for the course with code 4196?",
    "Which are the available classes for the Estructuras de datos course? Give me their codes",
    "Which are the prerequisites for Estructuras de datos?",
    "Which are the prerequisites for the course with code 4196?",
    "Which are the available schedules for class 1557?",
    "Are there any teachers called Oscar? Who?"
]

# Procesar cada pregunta con el sistema
'''
for question in questions:
    print(f"\nProcessing question: {question}")
    final_answer = execute_agent_until_success(question)
    print("<---- Final answer: ", final_answer)
    input("\nPress Enter to continue...")
'''

specific_question = "Which is the course code for Estructuras de datos?"
print(f"\nProcessing question: {specific_question}")
final_answer = execute_agent_until_success(specific_question)
print("<---- Final answer: ", final_answer)