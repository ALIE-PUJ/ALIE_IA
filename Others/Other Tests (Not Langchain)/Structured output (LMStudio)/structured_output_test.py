import requests
import json

# Define the API endpoint
url = "http://127.0.0.1:1234/v1/chat/completions"

# Define the request headers
headers = {
    "Content-Type": "application/json"
}

# Define the request payload
data = {
    "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful jokester."
        },
        {
            "role": "user",
            "content": "Tell me a joke."
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "joke_response",
            "strict": "true",
            "schema": {
                "type": "object",
                "properties": {
                    "joke": {
                        "type": "string"
                    }
                },
                "required": ["joke"]
            }
        }
    },
    "temperature": 0.7,
    "max_tokens": 50,
    "stream": False
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Parse the response
if response.status_code == 200:
    print("Response:", response.json())
    print("\n\n")
    content = response.json()["choices"][0]["message"]["content"]
    print("Content:", content)
else:
    print(f"Request failed with status code {response.status_code}")
