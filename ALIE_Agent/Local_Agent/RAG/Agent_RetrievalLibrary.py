import threading
import time
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Importe de librerias propias
from MongoDB_VectorSearchLibrary import *

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



# Herramientas de agente

# Función principal para manejar la lógica de cambio de modelo
def general_retrieval(user_input):
    primary_model_timeout = 10  # Tiempo en segundos para el modelo principal
    alternate_model_timeout = 10  # Tiempo en segundos para el modelo alternativo

    try:
        answer = retrieve_general_info(user_input, llm_primary, timeout=primary_model_timeout)
        if not answer:
            print("El modelo principal no respondió a tiempo o retornó None. Intentando con el modelo alternativo.")
            answer = retrieve_general_info(user_input, llm_alternate, timeout=alternate_model_timeout)
    except Exception as e:
        print(f"Error al obtener la respuesta: {e}")
        answer = None

    if not answer:
        print("No se pudo obtener una respuesta válida de ningún modelo.")
    
    return answer






# Some example questions
specific_question3 = "Dame informacion sobre las becas de la universidad. Cuales ofrece?"

# Get answer
answer = general_retrieval(specific_question3)
print("Answer = ", answer)
