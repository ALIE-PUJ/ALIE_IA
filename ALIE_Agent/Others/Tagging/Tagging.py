import os
import json
from datetime import datetime
from pymongo import MongoClient

def save_tag_to_mongo(user_prompt, agent_response, sentiment_tag, language):
    # Obtener la URI de conexión desde variables de entorno
    mongo_uri = os.getenv('MONGO_URI')
    
    # Si la URI no se encuentra, se construye
    if not mongo_uri:
        print("URI de conexión no encontrada. Construyendo URI de conexión...")
        user = os.getenv('MONGO_USER', 'admin')
        password = os.getenv('MONGO_PASS', 'admin123')
        host = os.getenv('MONGO_HOST', 'localhost')
        mongo_uri = f"mongodb://{user}:{password}@{host}:27017"
        print(f"URI de conexión construida: {mongo_uri}")
    else:
        print("URI de conexión encontrada: {mongo_uri}")
    
    # Inicializar el cliente de MongoDB
    client = MongoClient(mongo_uri)
    
    # Seleccionar la base de datos y la colección
    db = client['ALIE_DB']
    collection = db['InteraccionesPrevias']
    
    # Obtener la fecha y hora actual en el formato requerido
    last_updated = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Crear el documento con el formato requerido
    document = {
        "last_updated": last_updated,
        "sentiment_tag": sentiment_tag,
        "language": language,
        "user_prompt": user_prompt,
        "agent_response": agent_response
    }
    
    # Insertar el documento en la colección de MongoDB
    result = collection.insert_one(document)
    print("Documento insertado en MongoDB: ", result.inserted_id)

    # print("Documento insertado en MongoDB: ", document)
    
    # Eliminar el campo _id antes de guardar como JSON
    document.pop('_id', None)
    
    # Guardar el documento como archivo JSON con codificación UTF-8
    '''
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(document, file, ensure_ascii=False, indent=4)
    
    print(f"Documento insertado en MongoDB y guardado como {filename}")
    '''
    return document

# Ejemplo de uso
#tag_document = save_tag_to_mongo(user_prompt="¿Cuál es el clima hoy?", agent_response="El clima es soleado.", sentiment_tag="pos", language="es") # sentiment_tag can be 'pos', 'neg', or 'neu'
#print("Documento insertado en MongoDB: ", tag_document)
