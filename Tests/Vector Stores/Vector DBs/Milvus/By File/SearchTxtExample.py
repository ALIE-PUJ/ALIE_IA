# pip install --upgrade --quiet  langchain_milvus
# pymilvus 2.4.4. La version del paquete debe ser la misma que la especificada en la imagen del docker compose

# Imports
from langchain_community.document_loaders import TextLoader
from langchain_milvus.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

loader = TextLoader("Tests\Vector Stores\Vector DBs\Milvus\By File\Ejemplo.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

URI = "http://localhost:19530"

vector_db = Milvus.from_documents(
    docs,
    embedding=embedding_function,
    connection_args={"uri": URI},
)

query = "What did the president say about Ketanji Brown Jackson"
docs = vector_db.similarity_search(query)

print(docs[0].page_content)