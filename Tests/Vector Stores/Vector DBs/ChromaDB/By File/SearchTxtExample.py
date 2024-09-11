# import
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter

# pip install sentence-transformers
# pip install langchain-chroma

# load the document and split it into chunks
loader = TextLoader("Tests\Vector Stores\Vector DBs\ChromaDB\By File\Ejemplo.txt")
documents = loader.load()

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# Or Use OpenAI Embeddings

# load it into Chroma
vector_db = Chroma.from_documents(docs, embedding_function)

# query it
query = "What did the president say about Ketanji Brown Jackson"
docs = vector_db.similarity_search(query)

# print results
print(docs[0].page_content)