import time

# Local Agent imports (Library)
from Local_Agent.Local_FunctionCallerAgent import *
from Others.Translation.DeepTranslator_Translate import *

def process_user_query_and_translate(user_input, api_url, api_headers):
    """
    Process the user's query and translate it to English if it is not already in English.
    Also, return it in the original language if the query is not in English.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :return: The result of the query processing or None if the query is not in English.
    """
    # Detect language of the query
    user_language = detect_language(user_input)
    print(f"[POSTPROCESS - INFO] Detected User language: {user_language}")

    # Translate the query to English if it is not already in English
    if user_language != "en":
        print(f"[POSTPROCESS - INFO] User input not in English. Translating to English...")
        user_input = translate(user_input, "en") # translate to English

    answer = process_user_query(user_input, api_url, api_headers) # process the query

    if answer is not None and user_language != "en":
        print(f"[POSTPROCESS - INFO] Translating answer back to original language...")
        answer = translate(answer, user_language) # translate back to original user language
    return answer

def call_process_user_query_with_retries(user_input, api_url, api_headers, max_retries=3, delay=1):
    """
    Calls process_user_query and retries if the result is None.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param max_retries: Maximum number of retries if the result is None (default 3).
    :param delay: Delay between retries in seconds (default 1).
    :return: The result of process_user_query or None if all retries fail.
    """
    retries = 0
    answer = None
    start_time = time.time()  # Start the timer

    print("[LLM INFO] Posting to ", api_url)

    while retries < max_retries:
        answer = process_user_query_and_translate(user_input, api_url, api_headers)
        
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

# Define constants and run the functions
api_url_lmstudio = "http://127.0.0.1:1234/v1/chat/completions"
api_headers_lmstudio = {
    "Content-Type": "application/json"
}

# Define the content of the user input as a modifiable string
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

user_input = question16

# Run the function call and generate the final response
answer = call_process_user_query_with_retries(user_input = user_input, api_url = api_url_lmstudio, api_headers = api_headers_lmstudio) # Llamada a LmStudio
print("\n[Response] ---> Answer = ", answer)