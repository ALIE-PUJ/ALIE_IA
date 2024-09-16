import threading
import time
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Importe de librerias propias
from MongoDB_VectorSearchLibrary import *

# Traduccion
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



# Modelos
llm_primary = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
)

llm_alternate = ChatOpenAI(
    model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    temperature=0,
    max_tokens=None,
    timeout=None,
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)



# Funciones auxiliares

# Informacion general
def retrieve_general_info(user_input, llm, timeout=10): 
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    retriever = get_retriever()  # Get the retriever from the Vector Search Library (Milvus)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )

    def query_model():
        try:
            return qa({"question": user_input + ". Responde lo más rápido posible, pero con mucha calidad y tanto detalle como sea necesario, como enlaces o fuentes si pueden ser útiles."})
        except Exception as e:
            print(f"Error durante la consulta al modelo: {e}")
            return None

    def ejecutar_con_timeout(func, timeout=10):
        resultado = [None]  # Lista para almacenar el resultado de la función
        def wrapper():
            resultado[0] = func()

        hilo_funcion = threading.Thread(target=wrapper)
        hilo_funcion.start()
        hilo_funcion.join(timeout)

        if hilo_funcion.is_alive():
            print(f"La función no ha terminado después de {timeout} segundos, se cancelará.")
            return None
        return resultado[0]

    try:
        result = ejecutar_con_timeout(query_model, timeout)
        if result is None or 'answer' not in result:
            print("El modelo no proporcionó una respuesta válida.")
            return None
        return result['answer']
    except Exception as e:
        print(f"Error en retrieve_general_info: {e}")
        return None

# Cursos
def search_course_information_vectorStore(user_input: str, timeout=10):
    # Función que realiza la consulta
    def query_courses():
        try:
            filter_source = {"source": "Syllabus"}
            query = user_input
            result = query_vectordb(query, filter_source=filter_source, search_type="Multiple")
            return result
        except Exception as e:
            print(f"Error durante la consulta: {e}")
            return None

    # Función para ejecutar con límite de tiempo
    def ejecutar_con_timeout(func, timeout=10):
        resultado = [None]  # Lista para almacenar el resultado de la función
        def wrapper():
            resultado[0] = func()

        hilo_funcion = threading.Thread(target=wrapper)
        hilo_funcion.start()
        hilo_funcion.join(timeout)

        if hilo_funcion.is_alive():
            print(f"La función no ha terminado después de {timeout} segundos, se cancelará.")
            return None
        return resultado[0]

    try:
        # Detectar idioma del input del usuario
        user_language = detect_language(user_input)
        if user_language != "es":
            print(f"Idioma detectado: {user_language}. Traduciendo a español...")
            user_input = translate(user_input, "es")

        # Ejecutar la consulta con un timeout
        result = ejecutar_con_timeout(query_courses, timeout)

        # Si no hay resultados válidos o la consulta falló
        if result is None:
            print("No se obtuvo una respuesta válida.")
            return "No se encontraron cursos que coincidan con tu búsqueda."

        # Si la entrada original no estaba en español, traducir el resultado de vuelta al idioma original
        if user_language != "es":
            print(f"Traduciendo la respuesta al idioma original ({user_language})...")
            result = translate(result, user_language)

        return result

    except Exception as e:
        print(f"Error en search_course_information_vectorStore: {e}")
        return "Hubo un error al realizar la búsqueda. Intenta nuevamente más tarde."

    



# Herramientas de agente

# Función principal para manejar la lógica de cambio de modelo con manejo de fallos. Consultas generales
def general_retrieval(user_input):
    primary_model_timeout = 10  # Tiempo en segundos para el modelo principal
    alternate_model_timeout = 10  # Tiempo en segundos para el modelo alternativo

    try:
        # Traducir.
        user_language = detect_language(user_input)
        if user_language != "es":
            print(f"El idioma detectado es {user_language}. Traduciendo a español para mejorar la búsqueda vectorial...")
            user_input = translate(user_input, "es")

        answer = retrieve_general_info(user_input, llm_primary, timeout=primary_model_timeout)
        if not answer:
            print("El modelo principal no respondió a tiempo o retornó None. Intentando con el modelo alternativo.")
            answer = retrieve_general_info(user_input, llm_alternate, timeout=alternate_model_timeout)
    except Exception as e:
        print(f"Error al obtener la respuesta: {e}")
        answer = None

    if not answer:
        print("No se pudo obtener una respuesta válida de ningún modelo.")
    
    if user_language != "es":
        print(f"Traduciendo la respuesta al idioma original ({user_language})...")
        answer = translate(answer, user_language)

    return answer

# Función principal para manejar la lógica de cambio de modelo con manejo de fallos. Consultas de cursos
def course_retrieval_system(user_input):
    primary_timeout = 10  # Tiempo de espera para el primer intento
    alternate_timeout = 20  # Tiempo de espera para el modelo alternativo

    try:
        # Intentar buscar con la primera opción (primaria)
        result = search_course_information_vectorStore(user_input, timeout=primary_timeout)
        if not result or "No se encontraron cursos" in result:
            print("La búsqueda principal no dio resultados. Intentando con un modelo alternativo...")
            # Intentar una búsqueda alternativa si la principal falla
            result = search_course_information_vectorStore(user_input, timeout=alternate_timeout)
    except Exception as e:
        print(f"Error al obtener los cursos: {e}")
        result = "No se pudo obtener información sobre los cursos."

    return result





# Some example questions
specific_question1 = "Dame informacion sobre las becas de la universidad. Cuales ofrece?"
specific_question2 = "Which scholarships are available at the university?"
specific_question3 = "Que me puedes decir sobre el curso de estructuras de datos?"
specific_question4 = "What can you tell me about the data structures course?"

# General retrieval
#answer = general_retrieval(specific_question1)
#print("Answer = ", answer)

# Course retrieval
answer = course_retrieval_system(specific_question3)
print("Answer = ", answer)
