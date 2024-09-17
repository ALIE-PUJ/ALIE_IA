from flask import Flask, request, jsonify
import threading

# Imports de librerías propias
from AgentExecutor import *
from Others.Supervision.JSON_Detector import *
from Others.Tagging.TaggerChainLibrary import *

# Initialize the Flask app
app = Flask(__name__)

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
    tag_interaction_until_ok(user_prompts, agent_responses)
    print("Tagging completed.")

# Flask route for ALIE
@app.route('/ask', methods=['POST'])
def ALIE():
    # Extract the user question from the POST request
    data = request.json
    user_question = data.get('input')
    priority = data.get('priority')

    if priority == 'True':
        priority = True
    else:
        priority = False

    print("\033[34mReceived request with user question:", user_question, "and priority:", priority, "\033[0m")

    if not user_question:
        return jsonify({'error': 'No prompt provided'}), 400

    # 1. Process the query and get the answer
    alie_answer = process_query_ALIE(user_question, priority)

    # 3. Send response to the user
    response = {
        'answer': alie_answer
    }

    print("\033[34mSent answer to user:", response, "\033[0m")

    # 4. Start the background tagging process in a new thread
    threading.Thread(target=background_tagging, args=(user_question, alie_answer)).start()

    # Return the agent answer as JSON
    return jsonify(response)

# Entry point for the program
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)