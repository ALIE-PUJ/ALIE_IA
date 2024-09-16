# Functions - Tools
from langchain.agents import tool

# Importar libreria de Tagging a mongoDB
from Tagging import save_tag_to_mongo

# Tools
@tool("multiple_input_tag_interaction", return_direct=True)
def multiple_input_tag_interaction(user_prompt: str, agent_response: str, sentiment_tag: str, language: str) -> str:
    """
    Saves an interaction tag record to a MongoDB database.
    
    :param user_prompt: The question or prompt provided by the user.
    :param agent_response: The response given by the agent.
    :param sentiment_tag: The sentiment of the agent's response. This can be 'pos' (positive) or 'neg' (negative).
    :param language: The language in which the user prompt and agent response are written. For example, 'en' for English or 'es' for Spanish.

    :return: A message indicating that the document has been inserted into MongoDB and its content.
    """

    # Validate inputs
    if not user_prompt or not agent_response or not sentiment_tag or not language:
        raise ValueError("All parameters (user_prompt, agent_response, sentiment_tag, language) must be provided and non-empty.")

    if sentiment_tag not in ['pos', 'neg', 'neu']:
        raise ValueError("Invalid sentiment_tag. Must be one of 'pos', 'neg', 'neu'.")

    # Save the document as a JSON file with UTF-8 encoding
    file_content = save_tag_to_mongo(user_prompt=user_prompt, agent_response=agent_response, sentiment_tag=sentiment_tag, language=language)

    return f"Tag:Done. Tagging successfully saved to MongoDB and JSON file.\nFile content:\n{file_content}"

@tool("single_input_tag_interaction", return_direct=True)
def single_input_tag_interaction(data: dict) -> str:
    """
    Saves an interaction tag record to a MongoDB database using a single input dictionary.
    
    :param data: A dictionary containing the following keys:
        - 'user_prompt': The question or prompt provided by the user.
        - 'agent_response': The response given by the agent.
        - 'sentiment_tag': The sentiment of the agent's response. This can be 'pos' (positive) or 'neg' (negative).
        - 'language': The language in which the user prompt and agent response are written. For example, 'en' for English or 'es' for Spanish.
    
    :return: A message indicating that the document has been inserted into MongoDB and its content.
    """

    print("Data: ", data)

    # Extract data from the input dictionary
    user_prompt = data.get('user_prompt')
    agent_response = data.get('agent_response')
    sentiment_tag = data.get('sentiment_tag')
    language = data.get('language')

    # Validate inputs
    if not user_prompt or not agent_response or not sentiment_tag or not language:
        raise ValueError("All dictionary values (user_prompt, agent_response, sentiment_tag, language) must be provided and non-empty.")
    
    if sentiment_tag not in ['pos', 'neg', 'neu']:
        raise ValueError("Invalid sentiment_tag. Must be one of 'pos', 'neg', 'neu'.")

    # Save the document and get the JSON file content
    file_content = save_tag_to_mongo(user_prompt=user_prompt, agent_response=agent_response, sentiment_tag=sentiment_tag, language=language)
    
    return f"Tag:Done. Tagging successfully saved to MongoDB and JSON file.\nFile content:\n{file_content}"



# Ejemplo de uso
#response_message = single_input_tag_interaction({'user_prompt': "¿Cuál es el clima hoy?",'agent_response': "El clima es soleado.",'sentiment_tag': "pos",'language': "es"})
#print(response_message)