# Imports
import threading

# Imports de librerías propias
from AgentExecutor import *
from Others.Supervision.JSON_Detector import *
from Others.Tagging.TaggingAgentExecutor import *

# Flujo principal
# 1. Enviar query al agent_executor
# 2. Revisar que sea valida (No contiene JSON)
# 3. Enviar respuesta al usuario
# 4. Realizar tag

# Flujo principal
def process_query_ALIE(user_question, priority):
    while True:
        # 1. Enviar query al agent_executor
        agent_answer = get_answer(user_question, priority)
        print("\n[Response from agent executor (ALIE)] ---> Answer = ", agent_answer)

        # 2. Revisar si contiene JSON
        if not contains_json(agent_answer):
            # Si no contiene JSON, romper el bucle
            print("La respuesta no contiene JSON, continuando...")
            break

        # Si contiene JSON, repetir la solicitud
        print("La respuesta contiene JSON, volviendo a consultar con prioridad mayor...")
        priority = True

    return agent_answer

# Function to handle tagging in the background
def background_tagging(user_question, agent_answer):
    user_prompts = [user_question]
    agent_responses = [agent_answer]
    agent_tag(user_prompts, agent_responses)
    print("Tagging completed.")

# Main function that simulates user interaction
def ALIE(prompt, priority):
    # Simulate getting input from a user
    user_question = prompt

    # 1. Process the query and get the answer and 2. Check if it contains JSON
    alie_answer = process_query_ALIE(user_question, priority)

    # 3. Send response to the user
    print(f"\033[34m[ALIE] Answer: {alie_answer}\033[0m")

    # 4. Start the background tagging process in a new thread
    threading.Thread(target=background_tagging, args=(user_question, alie_answer)).start()

# Entry point for the program
if __name__ == "__main__":
    
    priority = False # Low priority
    ALIE("Which are the prerequisites for the course with code 4196?", priority)
