from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os
from deep_translator import GoogleTranslator
from langdetect import detect



# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")  # Clave API de Pinecone desde las variables de entorno
pc = Pinecone(api_key)

# Get your assistant.
assistant = pc.assistant.Assistant(
    assistant_name="alie", 
)



# Translate
def translate(query: str, target_language: str) -> str:
    """
    Translate a given query to the specified target language, regardless of the original language.

    This function uses the deep_translator library to convert the input query into the target language.
    It ensures that the query is translated properly to facilitate consistent processing.

    Parameters:
    query (str): The input query that needs to be translated.
    target_language (str): The language code for the target language (e.g., 'es' for Spanish, 'fr' for French).

    Returns:
    str: The translated query in the target language.
    """
    translator = GoogleTranslator(source='auto', target=target_language)
    translated = translator.translate(query)
    return translated

def detect_language(query: str) -> str:
    """
    Detect the language of the given query.

    This function uses the langdetect library to detect the language of the input query.

    Parameters:
    query (str): The input query whose language needs to be detected.

    Returns:
    str: The detected language code (e.g., 'en' for English, 'es' for Spanish).
    """
    detected_language = detect(query)
    return detected_language



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
    response = assistant.chat_completions(messages=chat_context)
    
    # Extract and return the response content
    content = response['choices'][0]['message']['content']
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
    response = assistant.chat_completions(messages=chat_context)
    
    # Extract and return the response content
    content = response['choices'][0]['message']['content']
    return content


# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":
    '''
    # Example usage
    query = 'Que becas ofrece la universidad?'
    response_content = general_retrieval(query)
    print("Response:", response_content)
    '''
