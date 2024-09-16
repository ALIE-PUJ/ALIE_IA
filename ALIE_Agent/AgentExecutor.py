import time
import threading

# Local imports (Library)
from Local_Agent.Local_FunctionCallerAgent import *
from Others.Translation.DeepTranslator_Translate import *

# Global timeout
global_timeout = 60  # 60 segundos

# Función genérica que ejecuta una función con timeout sobre un hilo
def ejecutar_con_timeout(func, args=(), kwargs=None, timeout=5):
    kwargs = kwargs if kwargs else {}
    resultado = [None]  # Lista para almacenar el resultado de la función

    def wrapper():
        resultado[0] = func(*args, **kwargs)

    hilo_funcion = threading.Thread(target=wrapper)
    hilo_funcion.start()
    hilo_funcion.join(timeout)

    if hilo_funcion.is_alive():
        print(f"La función no ha terminado después de {timeout} segundos, se cancelará.")
        return None
    return resultado[0]

def process_user_query_and_translate(user_input, api_url, api_headers, model, support_structured_output):
    """
    Process the user's query and translate it to English if it is not already in English.
    Also, return it in the original language if the query is not in English.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers for the API request.
    :param model: The model to use for processing the query.
    :param support_structured_output: Whether the model supports structured output.

    :return: The result of the query processing or None if the query is not in English.
    """
    # Detect language of the query
    user_language = detect_language(user_input)
    print(f"[POSTPROCESS - INFO] Detected User language: {user_language}")

    # Translate the query to English if it is not already in English
    if user_language != "en":
        print(f"[POSTPROCESS - INFO] User input not in English. Translating to English...")
        user_input = translate(user_input, "en") # translate to English

    answer = process_user_query(user_input, api_url, api_headers, model, support_structured_output) # process the query

    if answer is not None and user_language != "en":
        print(f"[POSTPROCESS - INFO] Translating answer back to original language...")
        answer = translate(answer, user_language) # translate back to original user language
    return answer

def call_process_user_query_with_retries(user_input, api_url, api_headers, model, support_structured_output, max_retries=3, delay=1):
    """
    Calls process_user_query and retries if the result is None.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers for the API request.
    :param model: The model to use for processing the query.
    :param support_structured_output: Whether the model supports structured output.
    :param max_retries: Maximum number of retries if the result is None (default 3).
    :param delay: Delay between retries in seconds (default 1).

    :return: The result of process_user_query or None if all retries fail.
    """
    retries = 0
    answer = None
    start_time = time.time()  # Start the timer

    print("[LLM INFO] Posting to ", api_url)

    while retries < max_retries:

        answer = process_user_query_and_translate(user_input, api_url, api_headers, model, support_structured_output) # Call With Translation
        # answer = process_user_query(user_input, api_url, api_headers, support_structured_output) # Call Without Translation

        if answer is not None:

            end_time = time.time()  # End the timer
            elapsed_time = end_time - start_time
            print(f"[POSTPROCESS - INFO] Successful on attempt {retries + 1}. Execution time: {elapsed_time:.2f} seconds.")
            return answer  # Exit loop if a valid answer is returned
        
        retries += 1
        print(f"[POSTPROCESS - INFO] Attempt {retries} returned None. Retrying in {delay} seconds...")
        time.sleep(delay)

    # If all retries failed
    end_time = time.time()  # End the timer after final attempt
    elapsed_time = end_time - start_time
    print(f"Max retries reached. Total execution time: {elapsed_time:.2f} seconds.")
    return None  # Return None if all retries fail




# Model data

# LmStudio
api_url_lmstudio = "http://127.0.0.1:1234/v1/chat/completions"
model_lmstudio = 'lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF'
api_headers_lmstudio = {
    "Content-Type": "application/json"
}
support_structured_output_lmstudio = True

# Groq
groq_api_key = os.getenv("GROQ_API_KEY", "NotFound")
model_groq = 'llama-3.1-70b-versatile'
api_url_groq = "https://api.groq.com/openai/v1/chat/completions"
api_headers_groq = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}
support_structured_output_groq = False



# Thread flow
def get_answer(user_input):
    # Intentar con LmStudio primero
    respuesta = ejecutar_con_timeout(
        call_process_user_query_with_retries,
        args=(user_input, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output_lmstudio),
        timeout=global_timeout
    )

    # Si no se obtuvo respuesta, intentar con Groq
    if respuesta is None:
        print("[INFO] LmStudio did not respond after 3 tries. Trying with Groq...")
        respuesta = ejecutar_con_timeout(
            call_process_user_query_with_retries,
            args=(user_input, api_url_groq, api_headers_groq, model_groq, support_structured_output_groq),
            timeout=global_timeout
        )

    # Si ninguno responde, devolver mensaje de error
    if respuesta is None:
        return "Both agents timed out before generating an answer. Try again later."

    return respuesta

# Traditional call structure (No threads)
# agent_answer = call_process_user_query_with_retries(user_input, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output_lmstudio) # Llamada a LmStudio
# agent_answer = call_process_user_query_with_retries(user_input, api_url_groq, api_headers_groq, model_groq, support_structured_output_groq) # Llamada a Groq# 



# Questions
question1 = "Is there any student called Luis? Who?"
question2 = "Which is the course code for the course named 'Estructuras de datos'?" # Hay que remover las tildes de las inserciones SQL.
question3 = "Which are the available classes for the course with code 4196?"
question4 = "Which are the available classes for the Estructuras de datos course? Give me their codes"
question5 = "Which are the prerequisites for Estructuras de datos?"
question6 = "Which are the prerequisites for the course with code 4196?"
question7 = "Which are the available schedules for class 1557?"
question8 = "Are there any teachers called Oscar? Who?"
question9 = "Hay algun estudiante llamado Luis? Quien?"
question10 = "Cual es el codigo de la materia llamada 'Estructuras de datos'?"
question11 = "Cuales son las clases disponibles para la materia con codigo 4196?"
question12 = "Cuales son las clases disponibles para la materia Estructuras de datos? Dame sus codigos"
question13 = "Cuales son los prerrequisitos para Estructuras de datos?"
question14 = "Cuales son los prerrequisitos para la materia con codigo 4196?"
question15 = "Cuales son los horarios disponibles para la clase 1557?"
question16 = "Hay algun profesor llamado Oscar? Quien?"
question17 = "What are the expected learning outcomes of estructuras de datos?"
question18 = "Cuales son los resultados de aprendizaje esperados de estructuras de datos?"
question19 = "What scholarships are available for students?"
question20 = "Cuales becas estan disponibles para los estudiantes?"
question21 = "Which are the carrer emphasis for systems engineering?"
question22 = "Cuales son las enfasis de carrera para ingenieria de sistemas?"
question23 = "Which are the available student groups?"
question24 = "Cuales son los semilleros disponibles?"
question25 = "What is ALIE?"

user_input = question24


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    
    agent_answer = get_answer(user_input)
    print("\n[Response from agent executor (AgentExecutor)] ---> Answer = ", agent_answer)    
    
