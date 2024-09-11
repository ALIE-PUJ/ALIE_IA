from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
import os

# Definir las rutas a las carpetas que contienen los archivos JSON
folders = [
    "Tests\\Vector Stores\\Vector DBs\\JSON\\Syllabus",
    "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\General",
    "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPrivada\\Q&A",
    "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\General",
    "Tests\\Vector Stores\\Vector DBs\\JSON\\InformacionPublica\\Q&A",
]  # Añade aquí todas las rutas de carpetas que necesites

# Definir el esquema JQ para extraer todo el contenido del JSON
jq_schema = "."  # Esto captura toda la información del archivo JSON

# Crear una lista para almacenar los documentos
all_documents = []

# Cargar todos los archivos JSON de cada carpeta
for folder_path in folders:
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            loader = JSONLoader(file_path, jq_schema=jq_schema, text_content=False)
            documents = loader.load()
            all_documents.extend(documents)

# Dividir los documentos en fragmentos
text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)  # Usar múltiplos de 2
docs = text_splitter.split_documents(all_documents)

# Crear la función de embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# LLM
# Cargar los fragmentos en Chroma
# pip install langchain-groq
from langchain_groq import ChatGroq
# Definir el modelo groq
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=5,
    # other params...
)

from langchain_openai import ChatOpenAI
# Definir el modelo
llm = ChatOpenAI(
    model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    temperature=0.9,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"    # organization="...",
    # other params...
)

# Compresor
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
compressor = LLMChainExtractor.from_llm(llm)

# Base retriever
from langchain_community.vectorstores import FAISS
retriever = FAISS.from_documents(docs, embedding_function).as_retriever()

# EmbeddingsFilter
from langchain.retrievers.document_compressors import EmbeddingsFilter
embeddings_filter = EmbeddingsFilter(embeddings=embedding_function, similarity_threshold=0.75)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter, base_retriever=retriever
)

# Realizar la consulta
query = "Cuales son los contenidos de programacion avanzada?"
result_docs = compression_retriever.invoke(query)

# Imprimir los resultados
if result_docs:
    print("\nSearch result = ", result_docs[0].page_content)
else:
    print("No se encontraron resultados para la consulta.")
