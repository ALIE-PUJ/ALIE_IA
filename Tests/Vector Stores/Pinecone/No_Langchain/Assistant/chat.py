from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")  # Clave API de Pinecone desde las variables de entorno
pc = Pinecone(api_key)

# Get your assistant.
assistant = pc.assistant.Assistant(
    assistant_name="alie", 
)

def get_assistant_response(argument):
    query = argument
    """
    Chat with the assistant and get a response based on the provided query.

    Args:
        query (str): The query to send to the assistant.

    Returns:
        str: The response content from the assistant.
    """
    # Prepare the chat context with the query
    chat_context = [Message(content=query + " Provee links si los hay")]
    
    # Get the response from the assistant
    response = assistant.chat_completions(messages=chat_context)
    
    # Extract and return the response content
    content = response['choices'][0]['message']['content']
    return content

# Example usage
query = 'Que becas ofrece la universidad?'
response_content = get_assistant_response(query)
print("Response:", response_content)
