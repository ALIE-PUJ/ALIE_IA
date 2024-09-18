from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import requests
from pinecone_plugins.assistant.control.core.client.exceptions import NotFoundException

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")  # API Key for Pinecone from environment variables
pc = Pinecone(api_key)

# Get your assistant. With error handling.
def get_assistant(name):
    try:
        return pc.assistant.Assistant(assistant_name=name)
    except NotFoundException:
        return None
    except Exception as e:
        print(f"Error obtaining assistant: {e}")
        return None

assistant = get_assistant("alie")



# Translate
def translate(query: str, target_language: str) -> str:
    """
    Translate a given query to the specified target language, regardless of the original language.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translated = translator.translate(query)
        return translated
    except Exception as e:
        print(f"Error translating query: {e}")
        return query # Return the original query if translation fails

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



# Pinecone Functions
def general_retrieval(argument):
    query = argument
    """
    Chat with the assistant and get a response based on the provided query.
    """
    if not assistant:
        return "Assistant not found. Please check the assistant name or create it if necessary."

    try:
        print("[PINECONE RAG] Sent query to Pinecone RAG:", query)
        # Detect the language of the query and translate it to Spanish if needed.
        query_language = detect_language(query)
        if query_language != "es":
            print("[PINECONE RAG] Original language is not Spanish, translating to Spanish...")
            query = translate(query, "es")
        print("[PINECONE RAG] Sent query to Pinecone RAG:", query)

        # Prepare the chat context with the query
        chat_context = [Message(content=query + " Provee links si los hay")]
        
        # Get the response from the assistant
        response = assistant.chat_completions(messages=chat_context)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            # Extract and verify the response content
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if content:
                return content
            else:
                return "Sorry, the response from the assistant was empty or invalid."
        else:
            return "Sorry, the response from the assistant was empty or invalid."
    
    except requests.RequestException as e:
        return f"Network error: {e}"
    except KeyError as e:
        return f"Error extracting response content: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def course_retrieval(argument):
    query = argument
    """
    Chat with the assistant and get a response based on the provided query.
    """
    if not assistant:
        return "Assistant not found. Please check the assistant name or create it if necessary."

    try:
        print("[PINECONE RAG] Sent query to Pinecone RAG:", query)
        # Detect the language of the query and translate it to Spanish if needed.
        query_language = detect_language(query)
        if query_language != "es":
            print("[PINECONE RAG] Original language is not Spanish, translating to Spanish...")
            query = translate(query, "es")
        print("[PINECONE RAG] Sent query to Pinecone RAG:", query)

        # Prepare the chat context with the query
        chat_context = [Message(content=query + " Provee links si los hay. Prioriza la informacion referente a Syllabus")]
        
        # Get the response from the assistant
        response = assistant.chat_completions(messages=chat_context)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            # Extract and verify the response content
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if content:
                return content
            else:
                return "Sorry, the response from the assistant was empty or invalid."
        else:
            return "Sorry, the response from the assistant was empty or invalid."
    
    except requests.RequestException as e:
        return f"Network error: {e}"
    except KeyError as e:
        return f"Error extracting response content: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE
if __name__ == "__main__":
    # Example usage
    query = 'Que becas ofrece la universidad?'
    response_content = general_retrieval(query)
    print("Response:", response_content)
