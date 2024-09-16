import requests
import json

# Library import depending on the context (Being used as a library or being executed directly)
from Tagging import *

# Set global parameters
temperature = 0
max_tokens = 1000

# Define the function registry dynamically
FUNCTIONS = {
    "save_tag_to_mongo": {
        "function_name": save_tag_to_mongo,
        "description": "Guarda una interacción en MongoDB con una etiqueta de sentimiento y el idioma del texto.",
        "arguments": {
            "user_prompt": "El mensaje del usuario que se quiere guardar.",
            "agent_response": "La respuesta del agente o sistema que se quiere guardar.",
            "sentiment_tag": "Etiqueta de sentimiento asociada a la interacción (pos, neg).",
            "language": "Idioma del texto (por ejemplo, 'es' para español)."
        },
        "example": {
            "query": "Guardar la interacción del usuario y la respuesta con etiqueta de sentimiento.",
            "expected": {
                "function_name": "save_tag_to_mongo",
                "arguments": {
                    "user_prompt": "¿Cuál es el clima hoy?",
                    "agent_response": "El clima es soleado.",
                    "sentiment_tag": "pos",
                    "language": "es"
                }
            }
        }
    }
}

def generate_system_prompt(functions):
    function_descriptions = (
        "For tagging, you can only execute the following function:\n"
        "Also, please do not modify the user's input when passing an argument, no matter the language. Do not try to make it shorter.\n"
        "Here are some example tags and their corresponding function calls:\n"
    )
    
    for func_name, func_info in functions.items():
        description = func_info["description"]
        arguments_desc = func_info["arguments"]  # Adjusted for the dictionary 'arguments'
        example_query = func_info["example"]["query"]
        example_expected = json.dumps(func_info["example"]["expected"], indent=2)
        
        # Format arguments description
        arguments_str = "\n".join([f"    - {arg}: {desc}" for arg, desc in arguments_desc.items()])
        
        function_descriptions += (
            f"- {func_name}: {description}\n"
            f"  Arguments:\n{arguments_str}\n"
            f"  Example Query: {example_query}\n"
            f"  Example Expected Response: {example_expected}\n"
        )
    
    return function_descriptions

def handle_function_call(tag_input, url, headers, functions, model, support_structured_output):
    """
    Handles the initial function call based on user input and processes the response.
    
    :param tag_input: The input tag to process.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param functions: El diccionario de funciones disponibles.
    :param model: El nombre o ID del modelo para usar en las solicitudes de la API.
    :param support_structured_output: Un booleano que indica si el modelo o la API admiten salida estructurada.
    :return: The name of the function called and the formatted message for the final response., or None if the request fails.
    """

    print("[INFO] ---> Tag Input to process:", tag_input)

    system_prompt = generate_system_prompt(functions)
    # print(f"[DEBUG] ---> System Prompt: {system_prompt}")

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
                "content": tag_input  # Use the modifiable string `tag_input`
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
                "content": system_prompt + ". Tag the most relevant part of the interaction. Be very objective"  # Use the dynamically generated system prompt
            },
            {
                "role": "user",
                "content": tag_input  # Use the modifiable string `tag_input`
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
                    return None, None
            except Exception as e:
                print(f"[ERROR] ---> Postprocessing failed: {e}")
                return None, None

        # Skip postprocessing if structured output is supported
        result_json = json.loads(result)

        function_name = result_json["function_name"]
        arguments = result_json["arguments"]  # Ensure this contains user_prompt, agent_response, sentiment_tag, and language

        # Call the corresponding function based on the name returned by the model
        if function_name in functions:
            func = functions[function_name]["function_name"]
            
            func_args = {
                "user_prompt": arguments.get("user_prompt"),
                "agent_response": arguments.get("agent_response"),
                "sentiment_tag": arguments.get("sentiment_tag"),
                "language": arguments.get("language")
            }

            print("[DEBUG] ---> Function name: ", function_name, ". Function args: ", func_args)
            
            try:
                function_result = func(**func_args)
                print(f"[DEBUG] ---> Function executed: {function_name}, Result: {function_result}")

                return function_name, function_result
            except TypeError as e:
                print(f"---> [ERROR]: {e}. Check the arguments passed to {function_name}.")
                return None, None
        else:
            print(f"[ERROR] ---> Function '{function_name}' not recognized.")
            return None, None
    else:
        print(f"[ERROR] ---> Request failed with status code {response.status_code}")
        return None, None
    

def process_tag(user_prompts, agent_responses, api_url, api_headers, model, support_structured_output):
    """
    Processes a tag  by handling the function call and generating the final response.
    
    :param user_prompts: The list of user prompts to use for the tagging process.
    :param agent_responses: The list of agent responses to use for the tagging process.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers to include in the API request.
    :param model: The model name or ID to use for the API requests.
    :param support_structured_output: A boolean indicating whether the model or API supports structured output.
    """
    print("[ALIE LANGCHAIN DEBUG: START]")

    print("Generating input tag")
    interactions = []
    max_len = max(len(user_prompts), len(agent_responses))
        
    for i in range(max_len):
        if i < len(user_prompts):
            interactions.append(f"[User] {user_prompts[i]}")
        if i < len(agent_responses):
            interactions.append(f"[Agent] {agent_responses[i]}")
        
    # Unimos todas las interacciones en una sola entrada de texto
    combined_input = " ".join(interactions)
    print("[DEBUG] ----> Final tag input: ", combined_input)

    tag_input = combined_input

    try:
        # Run the function call and generate the final response
        function_name, final_message = handle_function_call(tag_input, api_url, api_headers, FUNCTIONS, model, support_structured_output)
        if final_message:
            final_response = final_message
            print("[ALIE LANGCHAIN DEBUG: END]")
            return final_response
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        print("[ALIE LANGCHAIN DEBUG END]")


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
    model_groq = 'llama3-8b-8192'
    api_url_groq = "https://api.groq.com/openai/v1/chat/completions"
    api_headers_groq = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    # Example interaction
    user_prompts = [
        "Hola, cual es el codigo de estructuras de datos",
        "4196",
        "Perfecto, gracias!"
    ]

    agent_responses = [
        "Cual curso? Especifica el codigo",
        "El curso de estructuras de datos es 4196"
    ]

    # Run the function call and generate the final response
    # Example usage for LmStudio:
    # print("\nProcessing tag using LmStudio...")
    # answer = process_tag(user_prompts, agent_responses, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output=True)
    # print("Answer = ", answer)

    # Example usage for Groq:
    print("\nProcessing tag using Groq...")
    answer = process_tag(user_prompts, agent_responses, api_url_groq, api_headers_groq, model_groq, support_structured_output=False)
    print("Answer = ", answer)
    
    