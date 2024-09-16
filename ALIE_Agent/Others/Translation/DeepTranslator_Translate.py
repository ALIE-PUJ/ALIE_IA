from deep_translator import GoogleTranslator
from langdetect import detect

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



# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":
    '''
    query = "Hello, how are you?"
    target_language = 'es'  # Specify the target language code here
    
    # Detect language of the query
    detected_language = detect_language(query)
    print(f"Detected language: {detected_language}")
    
    # Translate the query
    translated_query = translate(query, target_language)
    print(f"Original: {query}")
    print(f"Translated: {translated_query}")
    '''