import time as std_time
import threading
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import os

# Local imports (Library)
if __name__ == "__main__":
    # Direct execution, absolute import
    from Local_FunctionCallerAgent import *
else:
    # Imported as part of a package, relative import
    from .Local_FunctionCallerAgent import *

# Global timeout
global_timeout = int(os.getenv('GLOBAL_TIMEOUT', '120')) # 120 segundos por defecto
print(f"[Global timeout (AgentExecutor)]: {global_timeout} segundos")


# Función para traducir una consulta
def translate(query: str, target_language: str) -> str:
    """
    Translate a given query to the specified target language, regardless of the original language.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translated = translator.translate(query)
        return translated
    except Exception as e:
        print(f"Error translating query: {e}")
        return query # Return the original query if translation fails

# Función para traducir una consulta. EL LENGUAJE SE PUEDE AJUSTAR DEPENDIENDO DE LA PREFERENCIA O IMPLEMENTAR UNA API EXTERNA PARA LA DETECCION PRECISA DEL MISMO.
def translate_from_english_to_spanish(query: str) -> str:
    """
    Translate a given query to the specified target language, regardless of the original language.
    """
    print(f"[POSTPROCESS - INFO] Translating from English to Spanish...")
    try:
        translator = GoogleTranslator(source='en', target='es')
        translated = translator.translate(query)
        return translated
    except Exception as e:
        print(f"Error translating query: {e}")
        return query # Return the original query if translation fails

# Función para detectar el idioma de una consulta
def detect_language(query: str) -> str:
    """
    Detect the language of the given query.
    """
    try:
        detected_language = detect(query)

        if detected_language not in ["en", "es"]:
            print(f"Detected language: {detected_language}. Defaulting to Spanish.")
            return "es"

        return detected_language
    except LangDetectException as e:
        print(f"Error detecting language: {e}")
        return "es" # Default to Spanish if language detection fails

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
    answer_language = detect_language(answer)
    print(f"[POSTPROCESS - INFO] Detected Answer language: {answer_language}")



    # Temporal bug fix. Always translate from english back to spanish
    answer = translate_from_english_to_spanish(answer)
    answer_language = detect_language(answer)
    print(f"[POSTPROCESS - INFO] Detected Answer language AFTER TRANSLATION: {answer_language}")



    if answer is not None and answer_language != 'es': # If the answer is not None and the language is different from the user language
        print(f"[POSTPROCESS - INFO] The answer is not in the user's original language. Translating answer back to original language...")
        answer = translate(answer, 'es') # translate back to original user language
    else:
        print(f"[POSTPROCESS - INFO] The answer is in the user's original language '{user_language}'. Returning answer...")

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
    start_time = std_time.time()  # Start the timer

    print("[LLM INFO] Posting to ", api_url)

    while retries < max_retries:

        answer = process_user_query_and_translate(user_input, api_url, api_headers, model, support_structured_output) # Call With Translation
        # answer = process_user_query(user_input, api_url, api_headers, model, support_structured_output) # Call Without Translation

        if answer is not None:

            end_time = std_time.time()  # End the timer
            elapsed_time = end_time - start_time
            print(f"[POSTPROCESS - INFO] Successful on attempt {retries + 1}. Execution time: {elapsed_time:.2f} seconds.")
            return answer  # Exit loop if a valid answer is returned
        
        retries += 1
        print(f"[POSTPROCESS - INFO] Attempt {retries} returned None. Retrying in {delay} seconds...")
        std_time.sleep(delay)

    # If all retries failed
    end_time = std_time.time()  # End the timer after final attempt
    elapsed_time = end_time - start_time
    print(f"Max retries reached. Total execution time: {elapsed_time:.2f} seconds.")
    return None  # Return None if all retries fail




# Model data

# LmStudio
# Obtiene la base de la URL de una variable de entorno, o usa '127.0.0.1' si no existe
host = os.getenv('LMSTUDIO_HOST', '127.0.0.1')
# Obtiene el puerto de una variable de entorno, o usa '1234' si no existe
port = os.getenv('LMSTUDIO_PORT', '1234')

# Concatena la ruta final para obtener la URL completa
api_url_lmstudio = f"http://{host}:{port}/v1/chat/completions"
print(f"[INFO - AgentExecutor] LmStudio API URL: {api_url_lmstudio}")
model_lmstudio = 'luisalejandrobf/ALIE_Model-Q4_K_M-GGUF'
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
def get_answer(user_input, priority):

    respuesta = None

    if priority == False:
        print("[INFO] Low priority. Trying LmStudio.")
        # Intentar con LmStudio primero
        respuesta = ejecutar_con_timeout(
            call_process_user_query_with_retries,
            args=(user_input, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output_lmstudio),
            timeout=global_timeout
        )

    # Si no se obtuvo respuesta, intentar con Groq
    if respuesta is None:
        # Si es un retry (priority alto), intentar con Groq
        print("[INFO] High priority. Trying Groq.")

        print("[INFO] LmStudio did not respond after 3 tries. Trying with Groq...")
        respuesta = ejecutar_con_timeout(
            call_process_user_query_with_retries,
            args=(user_input, api_url_groq, api_headers_groq, model_groq, support_structured_output_groq),
            timeout=global_timeout
        )

    # Si ninguno responde, devolver mensaje de error
    if respuesta is None:
        # return "Both agents timed out before generating an answer. Try again later."
        return "Estamos resolviendo algunos inconvenientes. Intenta de nuevo en unos minutos."

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
question23 = "Which are the available student seedbeds?"
question24 = "Cuales son los semilleros disponibles?"
question25 = "What is ALIE?"

user_input = question24


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    '''
    priority = False # Low priority
    agent_answer = get_answer(user_input, priority)
    print("\n[Response from agent executor (AgentExecutor)] ---> Answer = ", agent_answer)    
    '''
