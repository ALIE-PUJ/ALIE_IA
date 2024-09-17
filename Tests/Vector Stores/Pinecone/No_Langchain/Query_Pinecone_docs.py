from pinecone import Pinecone
import os

api_key=os.environ.get("PINECONE_API_KEY")  # Set your Pinecone API key here
pc = Pinecone(api_key)
index = pc.Index("pinecone-general-index")

query = "Tell me about the tech company known as Apple"

x = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[query],
    parameters={
        "input_type": "query"
    }
)

results = index.query(
    namespace="ns1",
    vector=x[0].values,
    top_k=3,
    include_values=False,
    include_metadata=True
)

print(results)