from langchain_milvus.vectorstores import Milvus
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

# Cargar los fragmentos en Chroma
URI = "http://localhost:19530"

vector_db = Milvus.from_documents(
    docs,
    embedding=embedding_function,
    connection_args={"uri": URI},
)

# Realizar la consulta
query = "Que becas hay?"
result_docs = vector_db.similarity_search(query)

# Imprimir los resultados
if result_docs:
    print("\nSearch result = ", result_docs[0].page_content)
else:
    print("No se encontraron resultados para la consulta.")
