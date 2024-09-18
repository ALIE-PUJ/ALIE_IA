from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

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