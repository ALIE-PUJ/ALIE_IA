import requests
import json
from Library.DBsearchTests_Library import *  # Import all functions from the library

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
    Formatea la respuesta final basada en el input del usuario y el resultado de la función llamada.
    
    :param user_input: La pregunta o solicitud original del usuario.
    :param function_name: El nombre de la función llamada por el agente.
    :param result: El resultado de la función llamada.
    :return: Un mensaje formateado para presentar al usuario.
    """
    # Asegúrate de que el resultado esté en un formato legible
    if isinstance(result, dict):
        result = json.dumps(result, indent=2)
    
    # Crear un mensaje final
    final_message = (
        f"**Pregunta del Usuario:**\n{user_input}\n\n"
        f"**Resultado de la Función `{function_name}`:**\n{result}\n\n"
        f"**Ahora, proporciona una respuesta adecuada para el usuario basado en la información anterior.**"
    )
    
    return final_message

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

# Define the API endpoint
url = "http://127.0.0.1:1234/v1/chat/completions"

# Define the headers for the request
headers = {
    "Content-Type": "application/json"
}

# Generate the system prompt with available functions
system_prompt = generate_system_prompt(FUNCTIONS)

# Define the request payload
data = {
    "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
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
    "temperature": 0.5,
    "max_tokens": 100,
    "stream": False
}


# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Parse the response
if response.status_code == 200:
    print("Response:", response.json())
    
    # Get the content of the message
    result = response.json()["choices"][0]["message"]["content"]

    # Convert the content to JSON if necessary
    result_json = json.loads(result)

    # Access the deserialized data
    function_name = result_json["function_name"]
    arguments = result_json["arguments"]

    # Call the corresponding function based on the name returned by the model
    if function_name in FUNCTIONS:
        func = FUNCTIONS[function_name]["func"]
        
        # Prepare arguments for the function call
        func_args = {
            key: arguments["argument"]
            for key in FUNCTIONS[function_name]["args"]
        }
        
        # Call the function with the unpacked arguments
        try:
            function_result = func(**func_args)  # Call the function with the unpacked arguments
            
            # Prepare the final message
            final_message = format_response_for_llm(user_input, function_name, function_result)
            print(f"\n---> Function executed: {function_name}, Result: {result}")
 

            # Define the payload for the final response
            final_payload = {
                "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
                "messages": [
                    {
                        "role": "system",
                        "content": "Your task is to provide a final response to the user based on the provided details."
                    },
                    {
                        "role": "user",
                        "content": final_message  # Send the formatted message to the model
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 150,
                "stream": False
            }
            
            # Send the POST request to get the final response
            final_response = requests.post(url, headers=headers, data=json.dumps(final_payload))
            
            if final_response.status_code == 200:
                final_result = final_response.json()["choices"][0]["message"]["content"]
                print(f"\n---> Final Response to User:\n{final_result}")
            else:
                print(f"[ERROR] ---> Final response request failed with status code {final_response.status_code}")
        
        except TypeError as e:
            print(f"\n---> Error: {e}. Check the arguments passed to {function_name}.")
    else:
        print(f"\n---> Function '{function_name}' not recognized.")
else:
    print(f"[ERROR] ---> Request failed with status code {response.status_code}")
