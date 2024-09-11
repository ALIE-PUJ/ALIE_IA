from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain_groq import ChatGroq
from langchain.agents import tool
from datetime import date
import time as sys_time  # Renombrar el módulo `time` a `sys_time`
import os

# Set the maximum execution time for the main agent
max_execution_time = 1

# Herramientas
@tool
def get_current_date(text: str) -> str:
    """Returns today's date and hour, use this for any \
    questions related to knowing today's date. \
    The input should always be an empty string, \
    and this function will always return today's \
    date - any date mathematics should occur \
    outside this function."""
    return str(date.today())

from mysql.connector import connect, Error
@tool
def search_person_info_by_name(first_name: str) -> str:
    """
    Look up a person's information by their first name in the MySQL database. 
    It receives a string with the person's first name.
    The available information is: nombre, apellido, edad, ciudad, carrera, gustos, comida_favorita
    """
    print("Received first name: ", first_name)
    try:
        connection = connect(
            host="localhost",
            user="root",
            password="1234",
            database="langchain_db_tests"
        )
        cursor = connection.cursor()
        query = f"SELECT * FROM personas WHERE nombre = '{first_name}'"
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result_with_columns = [dict(zip(columns, row)) for row in result]
        cursor.close()
        connection.close()
        return str(result_with_columns)
    except Error as e:
        return f"Error: {e}"

# Definir los modelos
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
        [get_current_date, search_person_info_by_name], 
        llm_primary,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time  # Tiempo máximo de ejecución (en segundos) para el agente principal
    )

    agent_alternative_1 = initialize_agent(
        [get_current_date, search_person_info_by_name], 
        llm_alternative_1,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True,
        max_execution_time=max_execution_time  # Tiempo máximo de ejecución (en segundos) para el agente secundario
    )

    agent_alternative_2 = initialize_agent(
        [get_current_date, search_person_info_by_name], 
        llm_alternative_2,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True
    )

    return [agent_primary, agent_alternative_1, agent_alternative_2]

# Función para iniciar el contador de tiempo
def start_timer():
    return sys_time.time()

# Función para detener el contador de tiempo y calcular la duración
def stop_timer(start_time):
    elapsed_time = sys_time.time() - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")
    return elapsed_time

# Función para ejecutar el agente hasta obtener un resultado satisfactorio
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
                        question,
                    )
                )

                # Imprimir el resultado
                print("Answer: ", output)

                # Verificar si el resultado es exitoso
                if "Error:" not in output and "Agent stopped due to iteration limit or time limit" not in output:  # Cambia la lógica según cómo determines el éxito
                    print("Conversation complete and successful.")
                    stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                    return output  # Devolver el resultado exitoso

                elif "Agent stopped due to iteration limit or time limit" in output:
                    # Si la respuesta es debido a límite de iteración o tiempo, seguir intentando con el siguiente agente
                    print("Conversation: Agent stopped due to iteration limit or time limit. Trying next agent...")
                    raise Exception("Agent stopped due to iteration limit or time limit.")  # Forzar el cambio de agente

            except Exception as e:
                elapsed_time = sys_time.time() - start_time
                if elapsed_time >= max_execution_time:  # Tiempo máximo de ejecución (en segundos) para el agente principal
                    if attempt >= 5 and agent_number == 2:
                        print("Conversation:Failed. Task not completed. Priority level 2 reached and failed.")
                        stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                        return "Conversation:Failed. Task not completed. Priority level 2 reached and failed."
                    else:
                        print(f"\n[AGENT CHANGE] ----> Agent timed out after {elapsed_time:.2f} seconds with a max execution time of {max_execution_time} second(s). Switching to the next agent in the priority list.")
                        if fallback_agents:
                            next_agent = fallback_agents.pop(0)
                            return try_agent(next_agent, agent_number + 1, fallback_agents, attempt + 1)
                        else:
                            # Si llegamos al último agente, continuar intentando con él
                            print(f"[DEBUG] ----> Reached priority level 2. Ending with agent: {agent_number}")
                            stop_timer(start_time)  # Detener el contador de tiempo y mostrar la duración
                            return "Conversation:Failed. Task not completed. Priority level 2 reached and failed."
                print(f"An error occurred: {e}. Trying again...")  # Evitar que el agente explote

    # Iniciar la ejecución con el primer agente y cambiar en caso de error
    return try_agent(agents_with_priority.pop(0), 0, agents_with_priority)


# Ejemplo de uso
question = "Which is Luis career?"

# Llamar a la función para ejecutar el agente con múltiples intentos y agentes con prioridad
final_answer = execute_agent_until_success(question)
print("<---- Final answer: ", final_answer)
