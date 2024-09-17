from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os

# pip install --upgrade pinecone pinecone-plugin-assistant

api_key = os.getenv("PINECONE_API_KEY")  # Clave API de Pinecone desde las variables de entorno
pc = Pinecone(api_key)

# Get your assistant.
assistant = pc.assistant.Assistant(
    assistant_name="alie", 
)

# Chat with the assistant.
chat_context = [Message(content='Cual es el codigo de analisis de algoritmos?')]
response = assistant.chat_completions(messages=chat_context)

content = response['choices'][0]['message']['content'] # OpenAI Debug

print("Response:", content)