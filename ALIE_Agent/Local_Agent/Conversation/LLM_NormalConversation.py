import requests
import json
import os

# Set global parameters
temperature = 0
max_tokens = 1000

def generate_response(argument, url, headers, model):
    """
    Generates an LLM response.
    
    :param argument: El mensaje formateado para el modelo.
    :param url: La URL del endpoint de la API.
    :param headers: Los headers para la solicitud.
    :param model: El nombre o ID del modelo para usar en las solicitudes de la API.
    :return: The final response to the user., or None if the request fails.
    """

    message = argument
    print(f"[INFO] ---> Posting to generate a response to message: {message}")

    # print("Final message: ", message)

    final_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Your task is to craft a thoughtful and comprehensive response for the user. Please aim to be as clear and helpful as possible, ensuring that the information is both accurate and easy to understand. Be friendly, engaging and relatable."
            },
            {
                "role": "user",
                "content": message
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
    question1 = "Hello!"
    user_input = question1

    # Run the function call and generate the final response
    # Example usage for LmStudio:
    print("\nProcessing user query using LmStudio...")
    answer = generate_response(user_input, api_url_lmstudio, api_headers_lmstudio, model_lmstudio)
    print("Answer = ", answer)

    # Example usage for Groq:
    #print("\nProcessing user query using Groq...")
    #answer = generate_response(user_input, api_url_groq, api_headers_groq, model_groq)
    #print("Answer = ", answer)
    '''