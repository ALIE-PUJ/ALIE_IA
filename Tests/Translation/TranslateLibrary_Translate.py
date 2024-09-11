from langdetect import detect
from translate import Translator

# El código detecta el idioma del texto y lo traduce siempre al español. Puede ser util, ya que los modelos de lenguaje suelen responder en inglés, y responden mejor si se les pregunta en inglés.
# pip install langdetect translate

# La biblioteca googletrans es una mas rapida, pero requiere imports que no son compatibles con langchain_openai.

def detect_and_translate(text):
    # Detectar el idioma del texto
    detected_language = detect(text)
    print(f"Idioma detectado: {detected_language}")
    
    # Traducir el texto al español
    translator = Translator(to_lang="es")
    translation = translator.translate(text)
    
    return translation

# Ejemplo de uso de la función detect_and_translate
if __name__ == "__main__":
    text_to_translate = "This is a test text to be translated into Spanish."
    translated_text = detect_and_translate(text_to_translate)
    print(f"Texto traducido: {translated_text}")
