import requests
import json

# Library import depending on the context (Being used as a library or being executed directly)
if __name__ == "__main__":
    # Direct execution, absolute import
    from RelationalDB.DBsearchTests_Library import *
    from RAG.Pinecone_Chat import *
else:
    # Imported as part of a package, relative import
    from .RelationalDB.DBsearchTests_Library import *
    from .RAG.Pinecone_Chat import *

# Set global parameters
temperature = 0
max_tokens = 1000

# Define the function registry dynamically
FUNCTIONS = {
    "get_students_by_name": {
        "function_name": get_students_by_name,
        "description": "Searches for students by their name.",
        "argument": "The name of the student to search for.",
        "example": {
            "query": "Is there any student called Luis? Who?",
            "expected": {
                "function_name": "get_students_by_name",
                "argument": "Luis"
            }
        }
    },
    "get_course_by_name": {
        "function_name": get_course_by_name,
        "description": "Searches a course basic information by its name. It provides the course code and description. For more detailed information like contents, expected learning outcomes, etc. Use course_retrieval.",
        "argument": "The name of the course to search for.",
        "example": {
            "query": "Which is the course code for the course named 'Estructuras de datos'?",
            "expected": {
                "function_name": "get_course_by_name",
                "argument": "Estructuras de datos"
            }
        }
    },
    "get_classes_by_course_code": {
        "function_name": get_classes_by_course_code,
        "description": "Searches for classes by course code.",
        "argument": "The code of the course to search for.",
        "example": {
            "query": "Which are the available classes for the course with code 4196?",
            "expected": {
                "function_name": "get_classes_by_course_code",
                "argument": "4196"
            }
        }
    },
    "get_classes_by_course_name": {
        "function_name": get_classes_by_course_name,
        "description": "Searches for classes by course name.",
        "argument": "The name of the course to search for.",
        "example": {
            "query": "Which are the available classes for the Estructuras de datos course? Give me their codes",
            "expected": {
                "function_name": "get_classes_by_course_name",
                "argument": "Estructuras de datos"
            }
        }
    },
    "get_class_by_code": {
        "function_name": get_class_by_code,
        "description": "Searches for a class by its code.",
        "argument": "The code of the class to search for.",
        "example": {
            "query": "What can you tell me about class 1557?",
            "expected": {
                "function_name": "get_class_by_code",
                "argument": "1557"
            }
        }
    },
    "get_prerequisites_by_course_name": {
        "function_name": get_prerequisites_by_course_name,
        "description": "Searches for prerequisites of a course by course name. Not code. For that, use get_prerequisites_by_course_code",
        "argument": "The name of the course to search for prerequisites.",
        "example": {
            "query": "Which are the prerequisites for Estructuras de datos?",
            "expected": {
                "function_name": "get_prerequisites_by_course_name",
                "argument": "Estructuras de datos"
            }
        }
    },
    "get_prerequisites_by_course_code": {
        "function_name": get_prerequisites_by_course_code,
        "description": "Searches for prerequisites of a course by course code. Not name. For that, use get_prerequisites_by_course_name",
        "argument": "The code of the course to search for prerequisites.",
        "example": {
            "query": "Which are the prerequisites for the course with code 4196?",
            "expected": {
                "function_name": "get_prerequisites_by_course_code",
                "argument": "4196"
            }
        }
    },
    "get_class_schedule": {
        "function_name": get_class_schedule,
        "description": "Searches for the schedule(s) of a class by its class ID.",
        "argument": "A single class ID to search for its schedule(s).",
        "example": {
            "query": "Which are the available schedules for class 1557?",
            "expected": {
                "function_name": "get_class_schedule",
                "argument": "1557"
            }
        }
    },
    "get_teacher_by_name": {
        "function_name": get_teacher_by_name,
        "description": "Searches for professors by their name.",
        "argument": "The name of the professor to search for.",
        "example": {
            "query": "Are there any teachers called Oscar? Who?",
            "expected": {
                "function_name": "get_teacher_by_name",
                "argument": "Oscar"
            }
        }
    },
    "general_retrieval": {
        "function_name": general_retrieval,
        "description": "Retrieves general information from the university vector store to search information to solve a query.",
        "user_input": "The user's input query that needs to be processed.",
        "argument": "The user's input query that needs to be processed.",
        "example": {
            "query": "What scholarships are available in the university?",
            "expected": {
                "function_name": "general_retrieval",
                "argument": "What scholarships are available in the university?"
            }
        }
    },
    "course_retrieval": {
        "function_name": course_retrieval,
        "description": "Searches for very detailed information about a course, like its contents, expected learning outcomes, etc. It is a more detailed search than get_course_by_name but is slower. It should only be used when asked for very detailed information.",
        "argument": "The query from the user to search for course-related information.",
        "user_input": "The query from the user to search for course-related information.",
        "example": {
            "query": "What are the contents of Estructuras de datos?",
            "expected": {
                "function_name": "course_retrieval_system",
                "argument": "What are the contents of Estructuras de datos?"
            }
        }
    }
}

def generate_system_prompt(functions):
    function_descriptions = (
        "You can execute the following functions:\n"
        "For each function, ensure to provide the 'argument' in the 'argument' field.\n"
        "Also, please do not modify the user's input when passing an argument, no matter the language. Do not try to make it shorter.\n"
        "Here are some example queries and their corresponding function calls:\n"
    )
    
    for func_name, func_info in functions.items():
        description = func_info["description"]
        argument_desc = func_info["argument"]  # Adjusted for the single 'argument' field
        example_query = func_info["example"]["query"]
        example_expected = json.dumps(func_info["example"]["expected"], indent=2)
        
        function_descriptions += (
            f"- {func_name}: {description}\n"
            f"  Argument: {argument_desc}\n"
            f"  Example Query: {example_query}\n"
            f"  Example Expected Response: {example_expected}\n"
        )
    
    # print("System prompt generado")
    
    return function_descriptions

def format_response_for_llm(user_input, function_name, result):
    """
    Formats the final response based on the user's input and the result of the called function.
    
    :param user_input: The original question or request from the user.
    :param function_name: The name of the function called by the agent.
    :param result: The result of the function call.
    :return: A formatted message to present to the user.
    """
    if isinstance(result, dict):
        result = json.dumps(result, indent=2)
    
    final_message = (
        f"**User Query:**\n{user_input}\n\n"
        f"**Function Result `{function_name}`:**\n{result}\n\n"
        f"**Now, provide a suitable response to the user based on the above information. Please, make it a natural language response so he does not know this post-processing is occuring**"
    )
    
    return final_message

def handle_function_call(user_input, url, headers, functions, model, support_structured_output):
    """
    Handles the initial function call based on user input and processes the response.
    
    :param user_input: La pregunta o solicitud original del usuario.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param functions: El diccionario de funciones disponibles.
    :param model: El nombre o ID del modelo para usar en las solicitudes de la API.
    :param support_structured_output: Un booleano que indica si el modelo o la API admiten salida estructurada.
    
    :return: El nombre de la función llamada, el mensaje final formateado o None si la solicitud falla.
    """

    print("[INFO] ---> User Input:", user_input)

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
                "content": user_input  # Use the modifiable string `user_input`
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
                "content": user_input  # Use the modifiable string `user_input`
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

        # Call the corresponding function based on the name returned by the model
        if function_name in functions:
            func = functions[function_name]["function_name"]
            
            func_args = {
                "argument": argument
            }

            print("[DEBUG] ---> Function name: ", function_name, ". Function args: ", func_args)
            
            try:
                function_result = func(**func_args)
                print(f"[DEBUG] ---> Function executed: {function_name}, Result: {function_result}")

                final_message = format_response_for_llm(user_input, function_name, function_result)

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
    

def generate_final_response(final_message, url, headers, model):
    """
    Generates the final response based on the formatted message from the function call.
    
    :param final_message: El mensaje formateado para el modelo.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param model: El nombre o ID del modelo para usar en las solicitudes de la API.
    :return: The final response to the user., or None if the request fails.
    """

    # print("Final message: ", final_message)

    final_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Your task is to craft a thoughtful and comprehensive final response for the user, incorporating all the details provided by the function result. Please aim to be as clear and helpful as possible, ensuring that the information is both accurate and easy to understand. Be friendly, engaging and relatable. Be sure to provide consistent information with what the result of the function says."
            },
            {
                "role": "user",
                "content": final_message
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    final_response = requests.post(url, headers=headers, data=json.dumps(final_payload))
    
    if final_response.status_code == 200:
        final_result = final_response.json()["choices"][0]["message"]["content"]
        print(f"[INFO] ---> Final Response by model: {final_result}")
        return final_result
    else:
        print(f"[ERROR] ---> Final response request failed with status code {final_response.status_code}")
        return None

def process_user_query(user_input, api_url, api_headers, model, support_structured_output):
    """
    Processes a user query by handling the function call and generating the final response.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers to include in the API request.
    :param model: The model name or ID to use for the API requests.
    :param support_structured_output: A boolean indicating whether the model or API supports structured output.
    """
    print("[ALIE LANGCHAIN DEBUG: START]")
    try:
        # Set temperature to 0 for function call
        temperature = 0
        # Run the function call and generate the final response
        function_name, final_message, function_result = handle_function_call(user_input, api_url, api_headers, FUNCTIONS, model, support_structured_output)
        if final_message:

            # DIRECT RETURNS LIST
            direct_return_function_names = ["course_retrieval", "general_retrieval"] # List of functions that return the final message directly
            if function_name in direct_return_function_names:
                print("[ALIE LANGCHAIN DEBUG: Found direct return function. Returning function_result.]")
                return function_result

            # If not in direct return list, continue with final response generation
            # Set temperature to 1 for final response
            temperature = 1
            print("[ALIE LANGCHAIN DEBUG: Function output requires post-processing. Returning final_response]")
            final_response = generate_final_response(final_message, api_url, api_headers, model)
            print("[ALIE LANGCHAIN DEBUG: END]")
            return final_response
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        print("[ALIE LANGCHAIN DEBUG END]")


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    '''
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

    # Define the content of the user input as a modifiable string
    question1 = "Is there any student called Luis? Who?"
    question2 = "Which is the course code for the course named 'Estructuras de datos'?" # Hay que remover las tildes de las inserciones SQL.
    question3 = "Which are the available classes for the course with code 4196?"
    question4 = "Which are the available classes for the Estructuras de datos course? Give me their codes"
    question5 = "Which are the prerequisites for Estructuras de datos?"
    question6 = "Which are the prerequisites for the course with code 4196?"
    question7 = "Which are the available schedules for class 1557?"
    question8 = "Are there any teachers called Oscar? Who?"

    user_input = question8

    # Run the function call and generate the final response
    # Example usage for LmStudio:
    #print("\nProcessing user query using LmStudio...")
    #answer = process_user_query(user_input, api_url_lmstudio, api_headers_lmstudio, model_lmstudio, support_structured_output=True)
    #print("Answer = ", answer)

    # Example usage for Groq:
    print("\nProcessing user query using Groq...")
    answer = process_user_query(user_input, api_url_groq, api_headers_groq, model_groq, support_structured_output=False)
    print("Answer = ", answer)
    '''
    