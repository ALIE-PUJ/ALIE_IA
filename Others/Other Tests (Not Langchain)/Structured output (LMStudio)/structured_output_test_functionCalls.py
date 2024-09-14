import requests
import json

# Define example functions
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

# Function registry
FUNCTIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply
}

def generate_system_prompt(functions):
    function_names = ', '.join(functions.keys())
    return f"You are an assistant that can execute one of the following functions based on the user's input: {function_names}. Make sure to return the function name and the arguments in the required format."

# Define the content of the user input as a modifiable string
user_input = "I want to substract 4 to 10."

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
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                },
                "required": ["function_name", "arguments"]
            }
        }
    },
    "temperature": 0.5,
    "max_tokens": 50,
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
        func = FUNCTIONS[function_name]
        result = func(arguments["a"], arguments["b"])
        print(f"Function executed: {function_name}, Result: {result}")
    else:
        print(f"Function '{function_name}' not recognized.")
else:
    print(f"Request failed with status code {response.status_code}")
