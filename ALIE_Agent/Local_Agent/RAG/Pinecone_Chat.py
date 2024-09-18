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

    Args:
        query (str): The query to send to the assistant.

    Returns:
        str: The response content from the assistant.
    """

    print("[PINECONE RAG] Sent query to Pinecone RAG:", query)
    # Detect the language of the query and translate it to Spanish if needed. (The DB is in Spanish)
    query_language = detect_language(query)
    if query_language != "es":
        print("[PINECONE RAG] original language is not Spanish, translating to Spanish...")
        query = translate(query, "es")
    print("[PINECONE RAG] Sent query to Pinecone RAG:", query)

    # Prepare the chat context with the query
    chat_context = [Message(content=query + " Provee links si los hay")]
    
    # Get the response from the assistant
    if assistant is not None:
        try:
            response = assistant.chat_completions(messages=chat_context)
        except Exception as e:
            print(f"Error during chat completion: {e}")
            return "No se encontró información relacionada con la consulta."
    else:
        print("Assistant not found.")
        return "No se encontró información relacionada con la consulta."
    
    # Extract and return the response content
    content = response['choices'][0]['message']['content']

    if content is None:
        content = "No se encontró información relacionada con la consulta."

    return content

def course_retrieval(argument):
    query = argument
    """
    Chat with the assistant and get a response based on the provided query.

    Args:
        query (str): The query to send to the assistant.

    Returns:
        str: The response content from the assistant.
    """

    print("[PINECONE RAG] Sent query to Pinecone RAG:", query)
    # Detect the language of the query and translate it to Spanish if needed. (The DB is in Spanish)
    query_language = detect_language(query)
    if query_language != "es":
        print("[PINECONE RAG] original language is not Spanish, translating to Spanish...")
        query = translate(query, "es")
    print("[PINECONE RAG] Sent query to Pinecone RAG:", query)

    # Prepare the chat context with the query
    chat_context = [Message(content=query + " Provee links si los hay. Prioriza la informacion referente a Syllabus")]
    
    # Get the response from the assistant
    if assistant is not None:
        try:
            response = assistant.chat_completions(messages=chat_context)
        except Exception as e:
            print(f"Error during chat completion: {e}")
            return "No se encontró información relacionada con la consulta."
    else:
        print("Assistant not found.")
        return "No se encontró información relacionada con la consulta."
    
    # Extract and return the response content
    content = response['choices'][0]['message']['content']

    if content is None:
        content = "No se encontró información relacionada con la consulta."

    return content

# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE
if __name__ == "__main__":


    # Example usage
    query = 'Que becas ofrece la universidad?'
    response_content = general_retrieval(query)
    print("Response:", response_content)
