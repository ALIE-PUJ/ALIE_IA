# Imports
from langchain_milvus.vectorstores import Milvus
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
import os
from uuid import uuid4

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

# Milvus URI
MILVUS_URI = ""



# Functions

def load_documents_from_folders(folders, jq_schema="."):
    """
    Load JSON documents from specified folders, assign sequential IDs, and manage them.
    """
    global vector_store, document_id_map
    
    all_documents = []
    print("Loading documents from folders...")
    
    # Initialize a sequential ID counter
    id_counter = 1
    
    for folder_path in folders:
        # Get the base folder name
        folder_base = os.path.basename(folder_path) 
        print(f"Processing folder: {folder_base}")  # Debugging line

        folder_id_map = {}  # Track document IDs for this folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                # Pass text_content=False if you don't want JSONLoader to treat content as string
                loader = JSONLoader(file_path, jq_schema=jq_schema, text_content=False)
                documents = loader.load()
                
                for doc in documents:
                    # Ensure page_content is properly converted to a string if needed
                    if not isinstance(doc.page_content, str):
                        doc.page_content = str(doc.page_content)  # Convert dict or other types to string
                    
                    doc_id = str(id_counter)  # Generate a sequential ID
                    id_counter += 1  # Increment the ID counter
                    doc.metadata = {"source": folder_base, "doc_id": doc_id}  # Use only the base folder name as source
                    all_documents.append(doc)
                    document_id_map[doc_id] = doc  # Map ID to document
                    folder_id_map[doc_id] = doc  # Map ID to document in this folder
        
        # Print document IDs for the current folder
        print(f"\nFolder: {folder_base}")
        print("Document IDs:", list(folder_id_map.keys()))
    
    # Create a vector store using the specified embedding model
    vector_store = create_vector_store(all_documents, embedding_model=selected_embedding_model)

    # Add documents to vector store. Already done by create_vector_store
    # vector_store.add_documents(documents=all_documents, ids=[doc.metadata["doc_id"] for doc in all_documents])
    
    print("Documents loaded and added to the vector store.")

def unload_documents_from_folder(folder):
    """
    Unload documents from a specified folder and remove their IDs from the vector store.
    """
    global document_id_map, vector_store

    # Get the folder name to compare with stored metadata
    folder_name = os.path.basename(folder)
    
    # Check if the folder exists in the stored documents
    folder_exists = any(doc.metadata.get('source') == folder_name for doc in document_id_map.values())
    
    if not folder_exists:
        print(f"No documents found for the folder '{folder}'.")
        return
    else:
        print(f"\nUnloading documents from folder '{folder}'...")
    
    # Get document IDs to remove
    ids_to_remove = [doc_id for doc_id, doc in document_id_map.items() if doc.metadata.get('source') == folder_name]
    
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
    
    print(f"\nDocuments from folder '{folder}' have been unloaded.")

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
    top_5_docs = filtered_docs[:5]

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

    def clean_query(query):
        """
        Limpia la consulta: elimina acentos, convierte a minúsculas y quita puntuación.
        """
        query = query.lower().strip()
        query = unidecode.unidecode(query)  # Eliminar acentos
        return query

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

    # Original query
    print("\n<----- Pre-Processing ----->")
    print(f"Original Query: {query}")

    # Construir el filtro_source

    # Si el filtro de fuente está presente y es de tipo "syllabus", filtrar por el nombre del curso
    if filter_source and filter_source.get("source") == "Syllabus":
        course_name = find_course_name(query)
        print("Found course: ", course_name)

        if course_name != "Curso no encontrado":
            print("Query'", query ,"'replaced for course name: ", course_name)
            query = course_name

        print(f"Filter source is 'Syllabus', applying course name filter: {course_name}")
    else:
        filter_source = filter_source
        # Se mantienen los filtros originales

    # Ejecutar la búsqueda según el tipo
    if search_type == "Single":
        print("Query = Single")
        print("<--------------------------->")
        # Realizar la búsqueda única y obtener el mejor resultado
        best_result = get_best_result(query, filter_source)
        print("\nget_best_result return:", best_result)
    elif search_type == "Multiple":
        print("Query = Multiple")
        print("<--------------------------->")
        # Realizar la búsqueda múltiple y obtener los 5 mejores resultados
        top_5_results = get_top_5_results(query, filter_source)
        print("\ntop_5_results return: ", top_5_results)
    else:
        print(f"Unknown search type: {search_type}")



# Main
if __name__ == '__main__':
        
    # Milvus URI
    MILVUS_URI = os.getenv('MILVUS_URI', 'http://localhost:19530')  # Si no se encuentra la variable de entorno, se asigna 'http://localhost:19530'

    # Example Folders
    folders = [
        "Tests\\Vector Stores\\Vector DBs\\JSON\\Syllabus",
        "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\General",
        "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\Q&A",
        "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\General",
        "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\Q&A",
    ]

    # Load and process documents
    load_documents_from_folders(folders)

    # Unload documents from a folder (Optional)
    #unload_documents_from_folder("Tests\\Vector Stores\\Vector DBs\\JSON\\Syllabus")
    #unload_documents_from_folder("Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\General")
    #unload_documents_from_folder("Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\Q&A")
    #unload_documents_from_folder("Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\General")
    #unload_documents_from_folder("Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\Q&A")

    # Perform a query and get the best result
    query1 = "Cuales son los contenidos de programacion avanzada?"
    query2 = "Cuantos creditos tiene estructura de datos?"
    query3 = "Cuáles son los prerequisitos para algebra lineal?"
    query4 = "Cómo se evalúa el curso de gestion de innovacion?"
    query5 = "Cuales son los libros recomendados para introduccion a la programacion?"
    query6 = "Cuales son los enfasis que ofrece la carrera?"
    query7 = "Que becas ofrece la universidad?"
    query8 = "Que grupos de investigacion ofrece la universidad?"
    query9 = "Que acreditaciones de calidad tiene la universidad?"

    selected_query = query2

    # filter_source = None
    filter_source = {"source": "Syllabus"}

    # Perform the search and get the best result
    #query_vectordb(selected_query, filter_source=filter_source, search_type="Single") # Single
    query_vectordb(selected_query, filter_source=None, search_type="Multiple") # Multiple

    # Si no hay filtro, se puede usar filter_source = None