import requests
import json
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

# Library import depending on the context (Being used as a library or being executed directly)
if __name__ == "__main__":
    # Direct execution, absolute import
    from Tagging import *
else:
    # Imported as part of a package, relative import
    from .Tagging import *

# Set global parameters
temperature = 0
max_tokens = 1000

# Define the function registry dynamically
FUNCTIONS = {
    "save_tag_to_mongo": {
        "function_name": save_tag_to_mongo,
        "description": "Saves the sentiment tag of a user-agent interaction to MongoDB.",
        "argument": "The prompt from the user.",
        "example": {
            "interaction": "[User] Hi, what is the code for data structures? [Agent] I have no idea.",
            "expected": {
                "function_name": "save_tag_to_mongo",
                "argument": "neg",
            }
        }
    }
}

def detect_language(query: str) -> str:
    """
    Detect the language of the given query.
    """
    try:
        detected_language = detect(query)
        return detected_language
    except LangDetectException as e:
        print(f"Error detecting language: {e}")
        return "es" # Default to Spanish if language detection fails

def generate_system_prompt(functions):
    function_descriptions = (
        "You can only execute the following function:\n"
        "Ensure to provide the 'argument' in the 'argument' field.\n"
        "Also, please do not modify the user's input when passing an argument, no matter the language. Do not try to make it shorter. You can only provide pos or neg as an argument, referring to a positive or negative interaction\n"
        "Here is a tagging example:\n"
    )
    
    for func_name, func_info in functions.items():
        description = func_info["description"]
        argument_desc = func_info["argument"]  # Adjusted for the single 'argument' field
        example_query = func_info["example"]["interaction"]
        example_expected = json.dumps(func_info["example"]["expected"], indent=2)
        
        function_descriptions += (
            f"- {func_name}: {description}\n"
            f"  Argument: {argument_desc}\n"
            f"  Example Interaction: {example_query}\n"
            f"  Example Expected Response: {example_expected}\n"
        )
    
    # print("System prompt generado")
    
    return function_descriptions

def handle_function_call(user_prompts, agent_responses, interaction, url, headers, functions, model, support_structured_output):
    """
    Handles the initial function call based on user input and processes the response.
    
    :param user_prompts: The user prompts to process.
    :param agent_responses: The agent responses to process.
    :param interaction: The conversation interaction to process.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param functions: El diccionario de funciones disponibles.
    :param model: El nombre o ID del modelo para usar en las solicitudes de la API.
    :param support_structured_output: Un booleano que indica si el modelo o la API admiten salida estructurada.
    
    :return: El nombre de la función llamada, el mensaje final formateado o None si la solicitud falla.
    """

    print("[INFO] ---> Interaction: ", interaction)

    system_prompt = generate_system_prompt(functions)
    print(f"[DEBUG] ---> System Prompt: {system_prompt}")

    # Define the request payload with structured output
    data_structured_output = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt  # Use the dynamically generated system prompt
            },
            {
                "role": "user",
                "content": interaction  # Use the modifiable string `interaction`
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "function_call",
                "strict": "true",
                "schema": {
                    "type": "object",
                    "properties": {
                        "function_name": {
                            "type": "string"
                        },
                        "argument": { 
                            "type": "string"
                        }
                    },
                    "required": ["function_name", "argument"]
                }
            }
        },
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    # Define the request payload without structured output
    data_not_structured_output = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt  # Use the dynamically generated system prompt
            },
            {
                "role": "user",
                "content": interaction  # Use the modifiable string `interaction`
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    if support_structured_output:
        data = data_structured_output
        print("[LLM INFO] Using structured output.")
    else:
        data = data_not_structured_output
        print("[LLM INFO] Using non-structured output.")

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Parse the response
    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        print(f"[DEBUG] ---> Response from the model (Structured Output): {result}")

        # Postprocess if structured output is not supported
        if not support_structured_output:
            try:
                # Encontrar el índice del primer '{' y el último '}'
                json_start = result.find("{")
                json_end = result.rfind("}")

                if json_start != -1 and json_end != -1:
                    # Extraer solo el bloque de JSON desde el primer '{' hasta el último '}'
                    result = result[json_start:json_end+1]
                else:
                    print("[ERROR] ---> No valid JSON found in the response.")
                    return None, None, None
            except Exception as e:
                print(f"[ERROR] ---> Postprocessing failed: {e}")
                return None, None, None

        # Skip postprocessing if structured output is supported
        result_json = json.loads(result)

        function_name = result_json["function_name"]
        argument = result_json["argument"]
        sentiment_tag = argument

        # Call the corresponding function based on the name returned by the model
        if function_name in functions:
            func = functions[function_name]["function_name"]

            # Create user and agent str messages
            user_interactions = [f"[{i + 1}] {prompt}" for i, prompt in enumerate(user_prompts)]
            agent_interactions = [f"[{i + 1}] {response}" for i, response in enumerate(agent_responses)]

            # Get the interaction language
            interaction_language = detect_language(user_prompts[0])
            print(f"[DEBUG] ---> Detected language for the interaction: {interaction_language}")

            # Tagging specific arguments
            func_args = {
                "user_prompt": user_interactions, # An str list of user prompts
                "agent_response": agent_interactions, # An str list of agent responses
                "sentiment_tag": sentiment_tag,
                "language": interaction_language
            }

            print("[DEBUG] ---> Function name: ", function_name, ". Function args: ", func_args)
            
            try:
                function_result = func(**func_args)
                print(f"[DEBUG] ---> Function executed: {function_name}, Result: {function_result}")

                final_message = "Tagging does not requiere result processing"

                return function_name, final_message, function_result
            except TypeError as e:
                print(f"---> [ERROR]: {e}. Check the arguments passed to {function_name}.")
                return None, None, None
        else:
            print(f"[ERROR] ---> Function '{function_name}' not recognized.")
            return None, None, None
    else:
        print(f"[ERROR] ---> Request failed with status code {response.status_code}")
        return None, None, None

def tag_interaction(user_prompts, agent_responses, api_url, api_headers, model, support_structured_output):
    """
    Processes a user query by handling the function call and generating the final response.
    
    :param user_prompts: The user prompts to process.
    :param agent_responses: The agent responses to process.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers to include in the API request.
    :param model: The model name or ID to use for the API requests.
    :param support_structured_output: A boolean indicating whether the model or API supports structured output.
    """
    print("[ALIE TAGGING DEBUG: START]")
    try:
        # Format the user prompts and agent responses into an interaction
        
        interactions = []
        max_len = max(len(user_prompts), len(agent_responses))
        
        for i in range(max_len):
            if i < len(user_prompts):
                interactions.append(f"[User] {user_prompts[i]}")
            if i < len(agent_responses):
                interactions.append(f"[Agent] {agent_responses[i]}")
        
        # Unimos todas las interacciones en una sola entrada de texto
        combined_input = " ".join(interactions)
        print("[DEBUG] ----> Final input: ", combined_input)


        # Set temperature to 0 for function call
        temperature = 0
        # Run the function call and generate the final response
        function_name, final_message, function_result = handle_function_call(user_prompts, agent_responses, combined_input, api_url, api_headers, FUNCTIONS, model, support_structured_output)

        if final_message:
            
            # function_result corresponds to the tagging result

            print("[ALIE TAGGING DEBUG: END]")
            return function_result
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        print("[ALIE TAGGING DEBUG END]")


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    # Model data

    # LmStudio
    api_url_lmstudio = "http://127.0.0.1:1234/v1/chat/completions"
    model_lmstudio = 'lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF'
    api_headers_lmstudio = {
        "Content-Type": "application/json"
    }

    # Groq
    groq_api_key = os.getenv("GROQ_API_KEY", "NotFound")
    model_groq = 'llama-3.1-70b-versatile'
    api_url_groq = "https://api.groq.com/openai/v1/chat/completions"
    api_headers_groq = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    '''
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



    # Run the function call and generate the final response
    # Example usage for LmStudio:
    #print("\nProcessing user query using LmStudio...")
    #answer = tag_interaction(user_prompts, agent_responses, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output=True)
    #print("Answer = ", answer)

    # Example usage for Groq:
    print("\nProcessing user query using Groq...")
    answer = tag_interaction(user_prompts, agent_responses, api_url_groq, api_headers_groq, model_groq, support_structured_output=False)
    print("Answer = ", answer)