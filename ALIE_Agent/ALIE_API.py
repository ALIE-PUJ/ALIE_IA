from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin # CORS for angular
import threading

# Imports de librerías propias
from Local_Agent.AgentExecutor import *
from Others.Supervision.JSON_Detector import *
from Others.Tagging.TaggingAgentExecutor import *

# Initialize the Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*"]}}) # Habilita CORS para la APP Flask. Necesario para que funcione adecuadamente con Angular

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
def background_tagging(user_question, agent_answer, priority):
    user_prompts = [user_question] # Turn into array
    agent_responses = [agent_answer] # Turn into array
    tag = agent_tag(user_prompts, agent_responses, priority)
    print("\033[33mTagging result:", tag, "\033[0m")
    print("Tagging completed.")

# Flask route for ALIE
@app.route('/alie', methods=['POST'])
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
    threading.Thread(target=background_tagging, args=(user_question, alie_answer, priority)).start()

    # Return the agent answer as JSON
    return jsonify(response)

# Entry point for the program
if __name__ == "__main__":

    import sys
    sys.stdout.reconfigure(line_buffering=True) # Para que los prints se muestren en tiempo real

    app.run(host='0.0.0.0', port=6000, threaded=True, debug=True)
    # Threaded = True para que el servidor pueda manejar múltiples solicitudes simultáneamente
    # Debug = True para que el servidor se reinicie automáticamente después de cada cambio en el código
    
    # Funciones disponibles:
    '''
    Nombre: get_students_by_name, Funcionalidad: Busca estudiantes por su nombre.
    Nombre: get_course_by_name, Funcionalidad: Busca información básica de un curso por su nombre.
    Nombre: get_course_by_code, Funcionalidad: Busca información básica de un curso por su código.
    Nombre: get_classes_by_course_code, Funcionalidad: Busca clases por el código de un curso.
    Nombre: get_classes_by_course_name, Funcionalidad: Busca clases por el nombre de un curso.
    Nombre: get_class_by_code, Funcionalidad: Busca una clase por su código.
    Nombre: get_prerequisites_by_course_name, Funcionalidad: Busca prerrequisitos de un curso por su nombre.
    Nombre: get_prerequisites_by_course_code, Funcionalidad: Busca prerrequisitos de un curso por su código.
    Nombre: get_class_schedule, Funcionalidad: Busca el horario de una clase por su ID.
    Nombre: get_teacher_by_name, Funcionalidad: Busca profesores por su nombre.
    Nombre: get_student_grades_by_period, Funcionalidad: Devuelve las notas de un estudiante organizadas por periodo.
    Nombre: get_student_courses, Funcionalidad: Devuelve todos los cursos que ha cursado un estudiante.
    Nombre: get_all_courses, Funcionalidad: Devuelve una lista de todos los cursos disponibles.
    Nombre: get_student_classes, Funcionalidad: Permite buscar las clases en las que un estudiante esta o ha estado inscrito, organizadas por periodo y mostrando asignatura y horario.
    Nombre: general_retrieval, Funcionalidad: Recupera información general de la universidad.
    Nombre: course_retrieval, Funcionalidad: Busca información detallada sobre un curso.
    Nombre: normal_conversation, Funcionalidad: Permite conversar de manera simple sin buscar información específica.
    '''