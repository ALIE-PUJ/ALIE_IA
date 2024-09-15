import requests
import json

# Library import depending on the context (Being used as a library or being executed directly)
if __name__ == "__main__":
    # Direct execution, absolute import
    from Library.DBsearchTests_Library import *
else:
    # Imported as part of a package, relative import
    from .Library.DBsearchTests_Library import *

# Set global parameters
model = 'lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf'
temperature = 0
max_tokens = 1000

# Define the function registry dynamically
FUNCTIONS = {
    "get_students_by_name": {
        "func": get_students_by_name,
        "description": "Searches for students by their name.",
        "args": {
            "argument": "The name of the student to search for."
        },
        "example": {
            "query": "Is there any student called Luis? Who?",
            "expected": {
                "function_name": "get_students_by_name",
                "arguments": {
                    "argument": "Luis"
                }
            }
        }
    },
    "get_course_by_name": {
        "func": get_course_by_name,
        "description": "Searches a course by its name. It provides info about the course, like its code and description.",
        "args": {
            "argument": "The name of the course to search for."
        },
        "example": {
            "query": "Which is the course code for the course named 'Estructuras de datos'?",
            "expected": {
                "function_name": "get_course_by_name",
                "arguments": {
                    "argument": "Estructuras de datos"
                }
            }
        }
    },
    "get_classes_by_course_code": {
        "func": get_classes_by_course_code,
        "description": "Searches for classes by course code.",
        "args": {
            "argument": "The code of the course to search for."
        },
        "example": {
            "query": "Which are the available classes for the course with code 4196?",
            "expected": {
                "function_name": "get_classes_by_course_code",
                "arguments": {
                    "argument": "4196"
                }
            }
        }
    },
    "get_classes_by_course_name": {
        "func": get_classes_by_course_name,
        "description": "Searches for classes by course name.",
        "args": {
            "argument": "The name of the course to search for."
        },
        "example": {
            "query": "Which are the available classes for the Estructuras de datos course? Give me their codes",
            "expected": {
                "function_name": "get_classes_by_course_name",
                "arguments": {
                    "argument": "Estructuras de datos"
                }
            }
        }
    },
    "get_class_by_code": {
        "func": get_class_by_code,
        "description": "Searches for a class by its code.",
        "args": {
            "argument": "The code of the class to search for."
        },
        "example": {
            "query": "Which are the prerequisites for Estructuras de datos?",
            "expected": {
                "function_name": "get_class_by_code",
                "arguments": {
                    "argument": "Estructuras de datos"
                }
            }
        }
    },
    "get_prerequisites_by_course_name": {
        "func": get_prerequisites_by_course_name,
        "description": "Searches for prerequisites of a course by course name.",
        "args": {
            "argument": "The name of the course to search for prerequisites."
        },
        "example": {
            "query": "Which are the prerequisites for Estructuras de datos?",
            "expected": {
                "function_name": "get_prerequisites_by_course_name",
                "arguments": {
                    "argument": "Estructuras de datos"
                }
            }
        }
    },
    "get_prerequisites_by_course_code": {
        "func": get_prerequisites_by_course_code,
        "description": "Searches for prerequisites of a course by course code.",
        "args": {
            "argument": "The code of the course to search for prerequisites."
        },
        "example": {
            "query": "Which are the prerequisites for the course with code 4196?",
            "expected": {
                "function_name": "get_prerequisites_by_course_code",
                "arguments": {
                    "argument": "4196"
                }
            }
        }
    },
    "get_class_schedule": {
        "func": get_class_schedule,
        "description": "Searches for the schedule(s) of a class by its class ID.",
        "args": {
            "argument": "A single class ID to search for its schedule(s)."
        },
        "example": {
            "query": "Which are the available schedules for class 1557?",
            "expected": {
                "function_name": "get_class_schedule",
                "arguments": {
                    "argument": "1557"
                }
            }
        }
    },
    "get_teacher_by_name": {
        "func": get_teacher_by_name,
        "description": "Searches for professors by their name.",
        "args": {
            "argument": "The name of the professor to search for."
        },
        "example": {
            "query": "Are there any teachers called Oscar? Who?",
            "expected": {
                "function_name": "get_teacher_by_name",
                "arguments": {
                    "argument": "Oscar"
                }
            }
        }
    }
}

def generate_system_prompt(functions):
    function_descriptions = (
        "You can execute the following functions:\n"
        "For each function, ensure to provide the 'argument' in the 'arguments' field.\n"
        "Also, please do not modify the user's input when passing an argument, no matter the language. Do not try to make it shorter.\n"
        "Here are some example queries and their corresponding function calls:\n"
    )
    for func_name, func_info in functions.items():
        description = func_info["description"]
        arg_desc = ", ".join([f"{arg_name}: {arg_desc}" for arg_name, arg_desc in func_info["args"].items()])
        example_query = func_info["example"]["query"]
        example_expected = json.dumps(func_info["example"]["expected"], indent=2)
        function_descriptions += (f"- {func_name}: {description}\n  Arguments: {arg_desc}\n"
                                  f"  Example Query: {example_query}\n"
                                  f"  Example Expected Response: {example_expected}\n")
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
        f"**Now, provide a suitable response to the user based on the above information. Please, make it a transparent and natural language response so he does not know this post-processing is occuring**"
    )
    
    return final_message

def handle_function_call(user_input, url, headers, functions):
    """
    Handles the initial function call based on user input and processes the response.
    
    :param user_input: La pregunta o solicitud original del usuario.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param functions: El diccionario de funciones disponibles.
    :return: The name of the function called and the formatted message for the final response., or None if the request fails.
    """

    print("[INFO] ---> User Input:", user_input)

    system_prompt = generate_system_prompt(functions)
    # print(f"[DEBUG] ---> System Prompt: {system_prompt}")

    # Define the request payload
    data = {
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
                        "arguments": {
                            "type": "object",
                            "properties": {
                                "argument": {
                                    "type": "string"
                                }
                            },
                            "required": ["argument"]
                        }
                    },
                    "required": ["function_name", "arguments"]
                }
            }
        },
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Parse the response
    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        print(f"[DEBUG] ---> Response from the model: {result}")

        result_json = json.loads(result)

        function_name = result_json["function_name"]
        arguments = result_json["arguments"]

        # Call the corresponding function based on the name returned by the model
        if function_name in functions:
            func = functions[function_name]["func"]
            
            func_args = {
                key: arguments["argument"]
                for key in functions[function_name]["args"]
            }
            
            try:
                function_result = func(**func_args)
                print(f"[DEBUG] ---> Function executed: {function_name}, Result: {result}")

                final_message = format_response_for_llm(user_input, function_name, function_result)

                return function_name, final_message
            except TypeError as e:
                print(f"---> [ERROR]: {e}. Check the arguments passed to {function_name}.")
                return None, None
        else:
            print(f"[ERROR] ---> Function '{function_name}' not recognized.")
            return None, None
    else:
        print(f"[ERROR] ---> Request failed with status code {response.status_code}")
        return None, None

def generate_final_response(final_message, url, headers):
    """
    Generates the final response based on the formatted message from the function call.
    
    :param final_message: El mensaje formateado para el modelo.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :return: The final response to the user., or None if the request fails.
    """
    final_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Your task is to provide a final response to the user based on the provided details."
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

def process_user_query(user_input, api_url, api_headers):
    """
    Processes a user query by handling the function call and generating the final response.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param api_headers: The headers to include in the API request.
    """
    print("[ALIE LANGCHAIN DEBUG: START]")
    try:
        # Run the function call and generate the final response
        function_name, final_message = handle_function_call(user_input, api_url, api_headers, FUNCTIONS)
        if final_message:
            final_response = generate_final_response(final_message, api_url, api_headers)
            print("[ALIE LANGCHAIN DEBUG: END]")
            return final_response
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        print("[ALIE LANGCHAIN DEBUG END]")


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    '''
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

    user_input = question8

    # Run the function call and generate the final response
    # Example usage:
    answer = process_user_query(user_input, api_url_lmstudio, api_headers_lmstudio)
    print("Answer = ", answer)
    '''