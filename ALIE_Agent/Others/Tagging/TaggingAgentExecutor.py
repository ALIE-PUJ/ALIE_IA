import time
import threading
import os

# Library import depending on the context (Being used as a library or being executed directly)
if __name__ == "__main__":
    # Direct execution, absolute import
    from  Local_TaggingCallerAgent import *
else:
    # Imported as part of a package, relative import
    from .Local_TaggingCallerAgent import *

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

def call_process_tag_with_retries(user_prompts, agent_responses, api_url, api_headers, model, support_structured_output, max_retries=3, delay=1):
    """
    Calls tag_interaction. Retries if the result is None.

    :param user_prompts: The user prompts to send to the model.
    :param agent_responses: The agent responses to send to the model.    
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers for the API request.
    :param model: The model to use for processing the tagging.
    :param support_structured_output: Whether the model supports structured output.
    :param max_retries: Maximum number of retries if the result is None (default 3).
    :param delay: Delay between retries in seconds (default 1).

    :return: The result of tag_interaction or None if all retries fail.
    """
    retries = 0
    answer = None
    start_time = time.time()  # Start the timer

    print("[LLM INFO] Posting to ", api_url)

    while retries < max_retries:

        answer = tag_interaction(user_prompts, agent_responses, api_url, api_headers, model, support_structured_output) # Call Without Translation

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
# Obtiene la base de la URL de una variable de entorno, o usa '127.0.0.1' si no existe
host = os.getenv('LMSTUDIO_HOST', '127.0.0.1')
# Obtiene el puerto de una variable de entorno, o usa '1234' si no existe
port = os.getenv('LMSTUDIO_PORT', '1234')

# Concatena la ruta final para obtener la URL completa
api_url_lmstudio = f"http://{host}:{port}/v1/chat/completions"
print(f"[INFO - Tagging] LmStudio API URL: {api_url_lmstudio}")
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
def agent_tag(user_prompts, agent_responses, priority):

    respuesta = None

    if priority == False:
        print("[INFO] Low priority. Trying LmStudio.")
        # Intentar con LmStudio primero
        respuesta = ejecutar_con_timeout(
            call_process_tag_with_retries,
            args=(user_prompts, agent_responses, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output_lmstudio),
            timeout=global_timeout
        )

    # Si no se obtuvo respuesta, intentar con Groq
    if respuesta is None:
        # Si es un retry (priority alto), intentar con Groq
        print("[INFO] High priority. Trying Groq.")

        print("[INFO] LmStudio did not respond after 3 tries. Trying with Groq...")
        respuesta = ejecutar_con_timeout(
            call_process_tag_with_retries,
            args=(user_prompts, agent_responses, api_url_groq, api_headers_groq, model_groq, support_structured_output_groq),
            timeout=global_timeout
        )

    # Si ninguno responde, devolver mensaje de error
    if respuesta is None:
        return "Both agents timed out before generating an answer. Try again later."

    return respuesta

# Traditional call structure (No threads)
# agent_answer = tag_interaction(user_prompts, agent_responses, api_url_groq, api_headers_groq, model_groq, support_structured_output=support_structured_output_groq) # Llamada a Groq
# agent_answer = tag_interaction(user_prompts, agent_responses, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output=support_structured_output_lmstudio) # Llamada a LmStudio



# Questions
'''
# Ex 1.
# Ejemplo de uso
# Arrays de usuario y agente
user_prompts = [
    "Hola, cual es el codigo de estructuras de datos",
    "estructuras de datos",
    "OK."
]
agent_responses = [
    "Cual curso?",
    "No tengo idea del codigo"
]
# Expected sentiment tag: neg
'''

# Ex 2.
# Ejemplo de uso
# Arrays de usuario y agente
user_prompts = [
    "Hola, cual es el codigo de estructuras de datos",
    "estructuras de datos",
    "OK, gracias!"
]
agent_responses = [
    "Cual curso?",
    "El codigo es 4196"
]
# Expected sentiment tag: pos



# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    '''
    priority = False # Low priority
    agent_answer = agent_tag(user_prompts, agent_responses, priority)
    print("\n[Response from agent TAG executor (AgentExecutor)] ---> Answer = ", agent_answer)
    '''