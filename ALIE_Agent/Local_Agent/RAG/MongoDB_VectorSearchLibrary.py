# Imports
from langchain_milvus.vectorstores import Milvus
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
import os
from uuid import uuid4
from langchain_community.document_loaders.mongodb import MongodbLoader
import unicodedata

# Global variables
vector_store = None
search_type = "mmr"
search_kwargs = {"k": 15, "fetch_k": 20}
selected_embedding_model = "all-MiniLM-L6-v2"
embedding_model_1 = "all-MiniLM-L6-v2"
embedding_model_2 = "facebook-dpr-ctx_encoder-single-nq-base"
embedding_model_3 = "roberta-large-nli-mean-tokens"

# Global arrays to hold document metadata
document_id_map = {}  # Dictionary to map document IDs to document objects

# URI
# Obtener la URI de conexión desde variables de entorno
mongo_uri = None
MILVUS_URI = None
selected_db_name = None # Nombre de la base de datos

is_initialized = False # Flag to check if the database has been initialized

# Functions

def remove_accents(text):
    """
    Remove accents from a given string.
    """
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn')

def load_documents_from_mongodb(collection_names):
    """
    Load JSON documents from specified MongoDB collections, assign sequential IDs, and manage them.
    """
    global vector_store, document_id_map
    
    all_documents = []
    print("Loading documents from MongoDB...")
    
    # Inicializar un contador de ID secuencial
    id_counter = 1
    
    for collection_name in collection_names:
        loader = MongodbLoader(
            connection_string=mongo_uri,
            db_name=selected_db_name,
            collection_name=collection_name
        )
        docs = loader.load()
        
        folder_id_map = {}  # Track document IDs for this collection
        
        for doc in docs:
            # Asegurar que el contenido de la página esté correctamente convertido a una cadena si es necesario
            if not isinstance(doc.page_content, str):
                doc.page_content = str(doc.page_content)  # Convertir dict o otros tipos a cadena
            
            # Eliminar las tildes del contenido del documento
            #print("Original content:", doc.page_content)
            doc.page_content = remove_accents(doc.page_content)
            #print("Content without accents:", doc.page_content)

            doc_id = str(id_counter)  # Generar un ID secuencial
            id_counter += 1  # Incrementar el contador de ID
            doc.metadata = {"source": collection_name, "doc_id": doc_id}  # Almacenar el nombre de la colección como fuente y generar un ID único
            all_documents.append(doc)
            document_id_map[doc_id] = doc  # Mapear ID a documento
            folder_id_map[doc_id] = doc  # Mapear ID a documento en esta colección
        
        # Imprimir IDs de documentos para la colección actual
        print(f"\nCollection: {collection_name}")
        print("Document IDs:", list(folder_id_map.keys()))

    # Dividir los documentos en fragmentos más pequeños para un mejor rendimiento de recuperación
    docs_splitter = split_documents(all_documents, 512, 64) # Usar múltiplos de 2
    
    # Crear una base de datos de vectores utilizando el modelo de embedding especificado
    vector_store = create_vector_store(docs_splitter, embedding_model=selected_embedding_model)

    print("Documents loaded and added to the vector store.")

def unload_documents_from_mongodb(collection_name):
    """
    Unload documents from a specified MongoDB collection and remove their IDs from the vector store.
    """
    global document_id_map, vector_store
    
    # Verificar si la colección existe en los documentos almacenados
    collection_exists = any(doc.metadata.get('source') == collection_name for doc in document_id_map.values())
    
    if not collection_exists:
        print(f"No documents found for the collection '{collection_name}'.")
        return
    else:
        print(f"\nUnloading documents from collection '{collection_name}'...")
    
    # Get document IDs to remove
    ids_to_remove = [doc_id for doc_id, doc in document_id_map.items() if doc.metadata.get('source') == collection_name]
    
    # Convert IDs to integers if the collection uses Int64 for IDs
    ids_to_remove_int = [int(doc_id) for doc_id in ids_to_remove]

    # Remove documents from the vector store
    if ids_to_remove_int:
        try:
            vector_store.delete(ids=ids_to_remove_int)
            print("Successfully deleted document IDs:", ids_to_remove_int)
            # Remove IDs from the ID map
            for doc_id in ids_to_remove:
                del document_id_map[doc_id]
        except ValueError as e:
            print(f"Error while deleting document IDs from vector store: {e}")
    
    print(f"\nDocuments from collection '{collection_name}' have been unloaded.")

def split_documents(documents, chunk_size, chunk_overlap):
    """
    Split documents into smaller chunks for better retrieval performance.
    """
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)

def create_vector_store(docs, embedding_model):
    """
    Create a Milvus vector database using the specified embedding model, assigning IDs to documents.
    """
    embedding_function = SentenceTransformerEmbeddings(model_name=embedding_model)

    # Extract IDs from document metadata
    ids = [doc.metadata["doc_id"] for doc in docs]
    print("Document IDs:", ids)
    
    # Create the Chroma vector store with IDs
    return Milvus.from_documents(docs, embedding=embedding_function, connection_args={"uri": MILVUS_URI}) # ids=ids no funciona con Milvus

def get_best_result(query, filter_source):
    """
    Retrieve documents matching the query, print all results, and return the best one.
    """
    global vector_store, search_type, search_kwargs

    print("\n<----- Search ----->")
    print("Search Parameters:")
    print(f"Filter Source: {filter_source}")
    print(f"Search Type: {search_type}")
    print(f"Search Kwargs: {search_kwargs}")
    
    retriever = vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
    
    # Retrieve all documents matching the query
    result_docs = retriever.invoke(query)
    print("Found", len(result_docs), "documents matching the query.")

    # Manually filter documents by the specified source if the filter is provided
    if filter_source and "source" in filter_source:
        filtered_docs = [doc for doc in result_docs if doc.metadata.get("source") == filter_source["source"]]
        print(f"Documents filtered by source: {filter_source['source']}")
    else:
        filtered_docs = result_docs
        print("No source filter applied.")

    # Get the first document (if any) from the filtered results
    single_doc = filtered_docs[0] if filtered_docs else None

    # Prepare a string to return the result
    result_str = f"\nResult for search '{query}':\n"
    if single_doc:
        result_str += f"\nDocument:\n"
        result_str += f"ID: {single_doc.metadata.get('doc_id', 'Unknown')}\n"
        result_str += f"Source: {single_doc.metadata.get('source', 'Unknown')}\n"
        result_str += f"Content: {single_doc.page_content}\n"
        result_str += "-" * 50 + "\n"
    else:
        result_str += "No results match the criteria.\n"

    return result_str

def get_top_5_results(query, filter_source):
    """
    Retrieve documents matching the query, filter by source, and return the top 5 as a formatted string.
    """
    global vector_store, search_type, search_kwargs

    print("\n<----- Search ----->")
    print("Search Parameters:")
    print(f"Filter Source: {filter_source}")
    print(f"Search Type: {search_type}")
    print(f"Search Kwargs: {search_kwargs}")
    
    retriever = vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
    
    # Retrieve all documents matching the query
    result_docs = retriever.invoke(query)
    print("Found", len(result_docs), "documents matching the query.")

    # Manually filter documents by the specified source if the filter is provided
    if filter_source and "source" in filter_source:
        filtered_docs = [doc for doc in result_docs if doc.metadata.get("source") == filter_source["source"]]
        print(f"Documents filtered by source: {filter_source['source']}")
    else:
        filtered_docs = result_docs
        print("No source filter applied.")

    # Get the top 5 documents
    top_5_docs = filtered_docs[:3]

    # Prepare a string to return the results
    result_str = f"\nTop 5 Results for search '{query}':\n"
    for i, doc in enumerate(top_5_docs, 1):
        result_str += f"\nResult doc #{i}:\n"
        result_str += f"ID: {doc.metadata.get('doc_id', 'Unknown')}\n"
        result_str += f"Source: {doc.metadata.get('source', 'Unknown')}\n"
        result_str += f"Content: {doc.page_content}\n"
        result_str += "-" * 50 + "\n"

    # If no documents match the criteria, return a message
    if not top_5_docs:
        result_str += "No results match the criteria.\n"
    
    return result_str



# Funcion de busqueda de cursos
import difflib
import unidecode

def clean_query(query):
    """
    Limpia la consulta: elimina acentos, convierte a minúsculas y quita puntuación.
    """
    query = query.lower().strip()
    query = unidecode.unidecode(query)  # Eliminar acentos
    return query

def find_course_name(query):
    """
    Procesa la consulta para extraer el nombre del curso al que hace referencia.
    Maneja variaciones ortográficas y consultas en inglés o con errores.
    """
    # Diccionario de cursos con posibles variaciones en español e inglés
    cursos_dict = {
        'calculo diferencial': 'Calculo Diferencial',
        'differential calculus': 'Calculo Diferencial',
        'logica y matematicas discretas': 'Logica y Matematicas Discretas',
        'logic and discrete mathematics': 'Logica y Matematicas Discretas',
        'introduccion a la programacion': 'Introduccion a la Programación',
        'introduction to programming': 'Introduccion a la Programación',
        'pensamiento sistemico': 'Pensamiento Sistemico',
        'systems thinking': 'Pensamiento Sistemico',
        'introduccion a la ingenieria': 'Introduccion a la Ingenieria',
        'introduction to engineering': 'Introduccion a la Ingenieria',
        'constitucion y derecho civil': 'Constitución y Derecho Civil',
        'constitution and civil law': 'Constitución y Derecho Civil',
        'calculo integral': 'Calculo Integral',
        'integral calculus': 'Calculo Integral',
        'fisica mecanica': 'Fisica Mecánica',
        'mechanical physics': 'Fisica Mecánica',
        'algebra lineal': 'Algebra Lineal',
        'linear algebra': 'Algebra Lineal',
        'programacion avanzada': 'Programación Avanzada',
        'advanced programming': 'Programación Avanzada',
        'ecuaciones diferenciales': 'Ecuaciones Diferenciales',
        'differential equations': 'Ecuaciones Diferenciales',
        'proyecto de diseño en ingenieria': 'Proyecto de Diseño en Ingenieria',
        'engineering design project': 'Proyecto de Diseño en Ingenieria',
        'significacion teologica': 'Significación Teologica',
        'theological significance': 'Significación Teologica',
        'calculo vectorial': 'Calculo Vectorial',
        'vector calculus': 'Calculo Vectorial',
        'probabilidad y estadistica': 'Probabilidad y Estadistica',
        'probability and statistics': 'Probabilidad y Estadistica',
        'analisis y diseño de software': 'Analisis y Diseño de Software',
        'software analysis and design': 'Analisis y Diseño de Software',
        'bases de datos': 'Bases de Datos',
        'databases': 'Bases de Datos',
        'arquitectura y organizacion del computador': 'Arquitectura y Organizacion del Computador',
        'computer architecture and organization': 'Arquitectura y Organizacion del Computador',
        'proyecto social universitario': 'Proyecto Social Universitario',
        'university social project': 'Proyecto Social Universitario',
        'estructuras de datos': 'Estructuras de Datos',
        'data structures': 'Estructuras de Datos',
        'analisis numerico': 'Analisis Numerico',
        'numerical analysis': 'Analisis Numerico',
        'fundamentos de ingenieria de software': 'Fundamentos de Ingenieria de Software',
        'software engineering fundamentals': 'Fundamentos de Ingenieria de Software',
        'sistemas operativos': 'Sistemas Operativos',
        'operating systems': 'Sistemas Operativos',
        'desarrollo web': 'Desarrollo Web',
        'web development': 'Desarrollo Web',
        'fundamentos de seguridad de la informacion': 'Fundamentos de Seguridad de la Informacion',
        'information security fundamentals': 'Fundamentos de Seguridad de la Informacion',
        'teoria de la computacion': 'Teoria de la Computacion',
        'theory of computation': 'Teoria de la Computacion',
        'sistemas de informacion': 'Sistemas de Informacion',
        'information systems': 'Sistemas de Informacion',
        'inteligencia artificial': 'Inteligencia Artificial',
        'artificial intelligence': 'Inteligencia Artificial',
        'gestion de proyectos de innovacion y emprendimiento de ti': 'Gestion de Proyectos de Innovacion y Emprendimiento de TI',
        'it innovation and entrepreneurship project management': 'Gestion de Proyectos de Innovacion y Emprendimiento de TI',
        'arquitectura de software': 'Arquitectura de Software',
        'software architecture': 'Arquitectura de Software',
        'tecnologias digitales emergentes': 'Tecnologias Digitales Emergentes',
        'emerging digital technologies': 'Tecnologias Digitales Emergentes',
        'gestion financiera de proyectos de ti': 'Gestion Financiera de Proyectos de TI',
        'financial management of it projects': 'Gestion Financiera de Proyectos de TI',
        'gerencia estrategica de ti': 'Gerencia Estrategica de TI',
        'strategic it management': 'Gerencia Estrategica de TI',
        'optimizacion y simulacion': 'Optimizacion y Simulacion',
        'optimization and simulation': 'Optimizacion y Simulacion',
        'planeacion de proyecto final': 'Planeacion de Proyecto Final',
        'final project planning': 'Planeacion de Proyecto Final',
        'proyecto de innovacion y emprendimiento': 'Proyecto de Innovacion y Emprendimiento',
        'innovation and entrepreneurship project': 'Proyecto de Innovacion y Emprendimiento',
        'comunicaciones y redes': 'Comunicaciones y Redes',
        'communications and networks': 'Comunicaciones y Redes',
        'introduccion a sistemas distribuidos': 'Introduccion a Sistemas Distribuidos',
        'introduction to distributed systems': 'Introduccion a Sistemas Distribuidos',
        'proyecto de grado': 'Proyecto de Grado',
        'thesis project': 'Proyecto de Grado',
        'etica en la era de la informacion': 'Etica en la Era de la Informacion',
        'ethics in the information age': 'Etica en la Era de la Informacion',
        'epistemologia de la ingenieria': 'Epistemologia de la Ingenieria',
        'epistemology of engineering': 'Epistemologia de la Ingenieria',
        'introduccion a la computacion movil': 'Introduccion a la Computacion Movil',
        'introduction to mobile computing': 'Introduccion a la Computacion Movil',
        'fe y compromiso del ingeniero': 'Fe y Compromiso del Ingeniero',
        'faith and commitment of the engineer': 'Fe y Compromiso del Ingeniero',
        'analisis de algoritmos': 'Analisis de algoritmos',
        'algorithm analysis': 'Analisis de algoritmos',
    }

    # Limpiar la consulta
    cleaned_query = clean_query(query)

    # Buscar el curso más cercano en el diccionario
    curso_match = difflib.get_close_matches(cleaned_query, cursos_dict.keys(), n=1, cutoff=0.5) # Ajusar cutoff si es necesario
    
    # Devolver el nombre oficial del curso si se encuentra una coincidencia
    if curso_match:
        return clean_query(cursos_dict[curso_match[0]])
    else:
        return "Curso no encontrado"



# Query externa (Libreria)
def query_vectordb(query, filter_source=None, search_type="Single"):
    """
    Realiza una consulta en la base de datos de vectores, aplica el filtro según la fuente,
    y devuelve los resultados basados en el tipo de búsqueda especificado.
    """
    global mongo_uri, MILVUS_URI, selected_db_name, is_initialized
    
    # Initialize database connection and load documents if not already done
    if not is_initialized:
        print("\n<----- Initialization ----->")

        MILVUS_URI = os.getenv('MILVUS_URI', 'http://localhost:19530')  # Si no se encuentra la variable de entorno, se asigna 'http://localhost:19530'

        mongo_uri = os.getenv('MONGO_URI')  
        selected_db_name = "ALIE_DB"  
        if not mongo_uri:
            user = os.getenv('MONGO_USER', 'admin')
            password = os.getenv('MONGO_PASS', 'admin123')
            host = os.getenv('MONGO_HOST', 'localhost')
            mongo_uri = f"mongodb://{user}:{password}@{host}:27017"
        collection_names = ["Syllabus", 
                            "InformacionPrivada_General", 
                            "InformacionPrivada_QA", 
                            "InformacionPublica_General", 
                            "InformacionPublica_QA"]
        load_documents_from_mongodb(collection_names)
        is_initialized = True
    else:
        print("Database already initialized. Skipping initialization.")

    print("\n<----- Pre-Processing ----->")
    print(f"Original Query: {query}")
    query = clean_query(query)
    print(f"Cleaned Query: {query}")

    if filter_source and filter_source.get("source") == "Syllabus":
        course_name = find_course_name(query)
        if course_name != "Curso no encontrado":
            print(f"Query replaced for course name: {course_name}")
            query = course_name
        else:
            print("Course not found. Using original query.")

    if search_type == "Single":
        return get_best_result(query, filter_source)
    elif search_type == "Multiple":
        return get_top_5_results(query, filter_source)
    else:
        raise ValueError(f"Unknown search type: {search_type}")

# Obtener retriever
def get_retriever():
    """
    Inicializa la base de datos y devuelve un objeto retriever para consultas.
    """
    global mongo_uri, MILVUS_URI, selected_db_name, is_initialized
    
    is_initialized = os.getenv('milvus_init', "False")

    if is_initialized == "True":
        is_initialized = True
    else:
        is_initialized = False

    # Initialize database connection and load documents if not already done
    if not is_initialized:
        print(f"[VECTOR STORE INFO] milvus_init is set to: {is_initialized}. Initializing database...")
        print("\n<----- Initialization ----->")

        MILVUS_URI = os.getenv('MILVUS_URI', 'http://localhost:19530')  # Si no se encuentra la variable de entorno, se asigna 'http://localhost:19530'

        mongo_uri = os.getenv('MONGO_URI')  
        selected_db_name = "ALIE_DB"  
        if not mongo_uri:
            user = os.getenv('MONGO_USER', 'admin')
            password = os.getenv('MONGO_PASS', 'admin123')
            host = os.getenv('MONGO_HOST', 'localhost')
            mongo_uri = f"mongodb://{user}:{password}@{host}:27017"
        collection_names = ["Syllabus", 
                            "InformacionPrivada_General", 
                            "InformacionPrivada_QA", 
                            "InformacionPublica_General", 
                            "InformacionPublica_QA"]
        load_documents_from_mongodb(collection_names)

        is_initialized = True
        # Asignar true a la variable de entorno milvus_init para no reinicializar la base de datos vectorial
        os.environ['milvus_init'] = "True"

    else:
        print("[VECTOR STORE INFO] milvus_init is set to: true. Database already initialized. Skipping initialization and returning retriever.")

    return vector_store.as_retriever()

# Ejemplo de uso
'''
result = query_vectordb("Cuales son los contenidos de programacion avanzada?", filter_source={"source": "Syllabus"}, search_type="Single")
print(result)

result = query_vectordb("Cuales son los contenidos de estructuras de datos?", filter_source={"source": "Syllabus"}, search_type="Multiple")
print(result)
'''
