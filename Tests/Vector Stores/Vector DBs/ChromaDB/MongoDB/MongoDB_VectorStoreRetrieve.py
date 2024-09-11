from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
import os

from langchain_community.document_loaders.mongodb import MongodbLoader
# pip install motor

# Obtener la URI de conexión desde variables de entorno
mongo_uri = os.getenv('MONGO_URI')  # Si no se encuentra la variable de entorno, se construye la URI

# Si la URI no se encuentra, se construye
if not mongo_uri:
    print("URI de conexión no encontrada. Construyendo URI de conexión...")
    user = os.getenv('MONGO_USER', 'admin')  # Si no se encuentra la variable de entorno, se asigna 'admin'
    password = os.getenv('MONGO_PASS', 'admin123')  # Si no se encuentra la variable de entorno, se asigna 'admin123'
    host = os.getenv('MONGO_HOST', 'localhost')  # 'mongodb' si se ejecuta en contenedor, 'localhost' si se ejecuta localmente
    mongo_uri = f"mongodb://{user}:{password}@{host}:27017"
    print("URI de conexión construida: ", mongo_uri)

# Cargar documentos desde MongoDB
# Lista de colecciones a cargar
collection_names = ["Syllabus", "InformacionPrivada_General", "InformacionPrivada_QA", "InformacionPublica_General", "InformacionPublica_QA"]  # Añade aquí todas las colecciones que quieras cargar

# Inicializar una lista para todos los documentos
all_docs = []

# Cargar documentos de cada colección
for collection_name in collection_names:
    loader = MongodbLoader(
        connection_string=mongo_uri,
        db_name="ALIE_DB",
        collection_name=collection_name,
    )
    docs = loader.load()
    all_docs.extend(docs)
    print(f"Documentos cargados desde {collection_name}: {len(docs)}")

print("Total de documentos cargados: ", len(all_docs))

# Dividir los documentos en fragmentos
text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0) # Usar multiplos de 2
docs_splitter = text_splitter.split_documents(docs)

# Crear la función de embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Cargar los fragmentos en Chroma
vector_db = Chroma.from_documents(docs_splitter, embedding_function)

# Realizar la consulta
query = "Cuales son los contenidos de la asignatura programacion avanzada?"
result_docs = vector_db.similarity_search(query)

# Imprimir los resultados
if result_docs:
    print("\nSearch result = ", result_docs[0].page_content)
else:
    print("No se encontraron resultados para la consulta.")