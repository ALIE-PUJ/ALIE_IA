from deep_translator import GoogleTranslator

def translate_to_spanish(query: str) -> str:
    """
    Translate a given query to Spanish, regardless of the original language.

    This function uses the deep_translator library to convert the input query into Spanish. 
    It ensures that the query is translated properly to facilitate consistent processing.

    Parameters:
    query (str): The input query that needs to be translated to Spanish.

    Returns:
    str: The translated query in Spanish.
    """
    translator = GoogleTranslator(source='auto', target='es')
    translated = translator.translate(query)
    return translated

# Test the translation function
if __name__ == "__main__":
    query = "Hello, how are you?"
    translated_query = translate_to_spanish(query)
    print(f"Original: {query}")
    print(f"Translated: {translated_query}")
