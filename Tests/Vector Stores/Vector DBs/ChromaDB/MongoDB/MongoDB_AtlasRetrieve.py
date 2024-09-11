# pip install -qU langchain-mongodb pymongo

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
import os

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# MongoDB Retrieve

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient

# Obtener la URI de conexión desde variables de entorno
mongo_uri = os.getenv('MONGO_URI')  # Si no se encuentra la variable de entorno, se construye la URI

# Si la URI no se encuentra, se construye
if not mongo_uri:
    print("URI de conexión no encontrada. Construyendo URI de conexión...")
    user = os.getenv('MONGO_USER', 'admin')  # Si no se encuentra la variable de entorno, se asigna 'admin'
    password = os.getenv('MONGO_PASS', 'admin123')  # Si no se encuentra la variable de entorno, se asigna 'admin123'
    host = os.getenv('MONGO_HOST', 'localhost')  # 'mongodb' si se ejecuta en contenedor, 'localhost' si se ejecuta localmente
    mongo_uri = f"mongodb://{user}:{password}@{host}:27017"

# initialize MongoDB python client
client = MongoClient(mongo_uri)

DB_NAME = "ALIE_DB"
COLLECTION_NAME = "Syllabus"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "langchain-test-index-vectorstores"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embedding_function,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

# query the vector store
query = "Cuales son los contenidos de programacion avanzada?"
docs = vector_store.similarity_search(query)

# print results
print(docs[0].page_content)