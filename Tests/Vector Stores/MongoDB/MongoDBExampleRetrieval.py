# pip install -qU langchain-mongodb pymongo
import os

# MongoDB Retrieve

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

# Select a database (replace 'your_database' with the actual database name)
db = client['ALIE_DB']

# Select a collection (replace 'your_collection' with the actual collection name)
collection = db['Syllabus']

# Make a simple query to retrieve all documents in the collection
documents = collection.find()

# Iterate through and print each document
for doc in documents:
    print(doc)