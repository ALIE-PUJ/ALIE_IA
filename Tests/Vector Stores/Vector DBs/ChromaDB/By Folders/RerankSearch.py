from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
import os
import numpy as np

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
            # Add metadata to each document
            for doc in documents:
                doc.metadata["source"] = os.path.basename(folder_path)
            all_documents.extend(documents)

# Dividir los documentos en fragmentos
text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=64)  # Usar múltiplos de 2
docs = text_splitter.split_documents(all_documents)

# Crear la función de embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Cargar los fragmentos en Chroma
vector_db = Chroma.from_documents(docs, embedding_function)

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

# Realizar la consulta inicial
query = "Cuales son los contenidos de programacion avanzada?"
result_docs_with_scores = vector_db.similarity_search_with_score(query)

# Obtener la función de embeddings para el reranking
rerank_embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# Obtener la función de embeddings para el reranking
rerank_embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
query_embedding = rerank_embedding_function.embed_query(query)

# Rerankear los resultados
reranked_results = []
for doc, score in result_docs_with_scores:
    doc_embedding = rerank_embedding_function.embed_documents([doc.page_content])[0]
    rerank_score = np.dot(query_embedding, doc_embedding) / (
        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
    )
    reranked_results.append((doc, rerank_score))

# Ordenar los resultados reranqueados
reranked_results.sort(key=lambda x: x[1], reverse=True)

# Imprimir los resultados reranqueados
if reranked_results:
    print("\nSearch result after reranking:")
    for doc, rerank_score in reranked_results:
        print("Source: ", doc.metadata.get("source", "Unknown"))
        print("Content: ", doc.page_content)
        print("Rerank Similarity Index: ", rerank_score)
        print("-" * 50)
else:
    print("No se encontraron resultados para la consulta.")
