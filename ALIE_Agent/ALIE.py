# Imports de librerías propias

from AgentExecutor import *
from Others.Supervision.JSON_Detector import *
from Others.Tagging.TaggerChainLibrary import *

# Flujo principal
# 1. Enviar query al agent_executor
# 2. Revisar que sea valida (No contiene JSON)
# 3. Enviar respuesta al usuario
# 4. Realizar tag

# Flujo principal
def process_query_ALIE(user_question):
    while True:
        # 1. Enviar query al agent_executor
        agent_answer = get_answer(user_question)
        print("\n[Response from agent executor (ALIE)] ---> Answer = ", agent_answer)

        # 2. Revisar si contiene JSON
        if not contains_json(agent_answer):
            # Si no contiene JSON, romper el bucle
            print("La respuesta no contiene JSON, continuando...")
            break

        # Si contiene JSON, repetir la solicitud
        print("La respuesta contiene JSON, volviendo a consultar...")

    # 3. Enviar respuesta al usuario
    # TO-DO with API

    # 4. Realizar tag
    user_prompts = [user_question]
    agent_responses = [agent_answer]
    tag_interaction_until_ok(user_prompts, agent_responses)

    return agent_answer

# Llamada a la función principal
final_answer = process_query_ALIE("Hay algun profesor llamado Oscar? Quien?")
print("Respuesta final:", final_answer)