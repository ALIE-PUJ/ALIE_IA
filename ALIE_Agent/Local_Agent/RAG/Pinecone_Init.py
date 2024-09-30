import os
import json
import io
import requests
from pymongo import MongoClient
import time

def get_mongo_uri():
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("URI de conexión no encontrada. Construyendo URI de conexión...")
        user = os.getenv('MONGO_USER', 'admin')
        password = os.getenv('MONGO_PASS', 'admin123')
        host = os.getenv('MONGO_HOST', 'localhost')
        mongo_uri = f"mongodb://{user}:{password}@{host}:27017"
    return mongo_uri

def connect_to_mongo(mongo_uri):
    return MongoClient(mongo_uri)

def setup_data_directory():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def list_assistants(api_key):
    assistants_url = "https://api.pinecone.io/assistant/assistants"
    response = requests.get(assistants_url, headers={"Api-Key": api_key})
    if response.status_code == 200:
        assistants = response.json().get('assistants', [])
        print(f"[GET LIST] Asistentes existentes: {assistants}")
        return assistants
    else:
        print(f"Error al listar asistentes. Código de estado: {response.status_code}, Respuesta: {response.text}")
        return []

def create_assistant_if_not_exists(api_key, assistant_name):
    assistants_url = "https://api.pinecone.io/assistant/assistants"
    assistants = list_assistants(api_key)
    for assistant in assistants:
        if assistant.get("name") == assistant_name:
            print(f"[CREATE] El asistente '{assistant_name}' ya existe.")
            return assistant

    print(f"[CREATE] '{assistant_name}' no existe. Creando asistente '{assistant_name}'...")
    create_assistant_url = assistants_url
    payload = {"name": assistant_name, "metadata": {}}
    response = requests.post(create_assistant_url, headers={"Api-Key": api_key, "Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        new_assistant = response.json()
        print(f"[CREATE] Asistente '{assistant_name}' creado exitosamente: {new_assistant}")
        print("Esperando 30 segundos para que el asistente se active...")
        time.sleep(30)
        return new_assistant
    else:
        print(f"Error al crear el asistente '{assistant_name}'. Código de estado: {response.status_code}, Respuesta: {response.text}")
        return None

def list_files_in_pinecone(api_key, base_url):
    response = requests.get(base_url, headers={"Api-Key": api_key})
    if response.status_code == 200:
        files = response.json().get('files', [])
        print(f"[FILE FETCH] Respuesta completa de la API: {files}")
        return files
    else:
        print(f"Error al listar archivos. Código de estado: {response.status_code}, Respuesta: {response.text}")
        return []

def delete_file_from_pinecone(api_key, base_url, file_id):
    delete_url = f"{base_url}/{file_id}"
    response = requests.delete(delete_url, headers={"Api-Key": api_key})
    if response.status_code == 200:
        print(f"[DELETE FILE] Archivo {file_id} eliminado exitosamente.")
    else:
        print(f"Error al eliminar archivo {file_id}. Código de estado: {response.status_code}, Respuesta: {response.text}")

def delete_file_by_name_from_pinecone(api_key, base_url, file_name):
    files = list_files_in_pinecone(api_key, base_url)
    for file_info in files:
        if isinstance(file_info, dict) and file_info.get('name') == file_name:
            file_id = file_info.get('id')
            if file_id:
                print(f"Eliminando archivo con nombre: {file_name} y ID: {file_id}")
                delete_file_from_pinecone(api_key, base_url, file_id)
                return
    print(f"No se encontró el archivo con nombre: {file_name}")

def upload_compiled_doc_to_pinecone(api_key, base_url, filepath, collection_name):
    with open(filepath, 'r', encoding='utf-8') as file:
        temp_file = io.StringIO(file.read())
        temp_file.seek(0)
    
    response = requests.post(base_url, headers={"Api-Key": api_key}, files={"file": (f"{collection_name}_compiled.txt", temp_file)})
    if response.status_code == 200:
        print(f"[UPLOAD FILE] Archivo '{collection_name}_compiled.txt' subido exitosamente. Response: {response.text}")
    else:
        print(f"Error al subir archivo '{collection_name}_compiled.txt'. Código de estado: {response.status_code}, Respuesta: {response.text}")
    
    temp_file.close()

def upload_collection_to_pinecone(db, collection_name, api_key, base_url, data_dir):
    collection = db[collection_name]
    documents = collection.find()
    
    compiled_filepath = os.path.join(data_dir, f"{collection_name}_compiled.txt")
    with open(compiled_filepath, 'w', encoding='utf-8') as compiled_file:
        for document in documents:
            compiled_file.write(json.dumps(document, ensure_ascii=False, default=str) + "\n")
    
    upload_compiled_doc_to_pinecone(api_key, base_url, compiled_filepath, collection_name)
    print(f"Datos de la colección '{collection_name}' subidos a Pinecone.")
    time.sleep(5)

def process_collections(db, collection_names, data_dir, api_key, base_url):
    for collection_name in collection_names:
        upload_collection_to_pinecone(db, collection_name, api_key, base_url, data_dir)

def reinit_collection(collection_name):
    # Paso 1: Obtener la URI de conexión a MongoDB y conectar a la base de datos
    mongo_uri = get_mongo_uri()
    client = connect_to_mongo(mongo_uri)
    db = client['ALIE_DB']
    collection_names = ["Syllabus", "InformacionPrivada_General", "InformacionPrivada_QA", "InformacionPublica_General", "InformacionPublica_QA"]

    # Paso 2: Configurar las variables de Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    assistant_name = os.getenv("ASSISTANT_NAME", "alie")
    base_url = f"https://prod-1-data.ke.pinecone.io/assistant/files/{assistant_name}"
    data_dir = setup_data_directory()

    # Paso 3: Crear el asistente en Pinecone si no existe
    create_assistant_if_not_exists(api_key, assistant_name)
    
    # Para eliminar un archivo por nombre:
    delete_file_by_name_from_pinecone(api_key, base_url, f"{collection_name}_compiled.txt")

    # Para procesar una sola colección:
    upload_collection_to_pinecone(db, collection_name, api_key, base_url, data_dir)

    # Finalización
    print("Compilación, eliminación de archivos antiguos y subida de nuevos documentos completada, Para la coleccion ", collection_name)

def main():

    print("Iniciando proceso de reinicio de la base de datos vectorial...")

    # Paso 1: Obtener la URI de conexión a MongoDB y conectar a la base de datos
    mongo_uri = get_mongo_uri()
    client = connect_to_mongo(mongo_uri)
    db = client['ALIE_DB']
    collection_names = ["Syllabus", "InformacionPrivada_General", "InformacionPrivada_QA", "InformacionPublica_General", "InformacionPublica_QA", "InteraccionesPrevias"]

    # Paso 2: Configurar las variables de Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    assistant_name = os.getenv("ASSISTANT_NAME", "alie")
    base_url = f"https://prod-1-data.ke.pinecone.io/assistant/files/{assistant_name}"
    data_dir = setup_data_directory()

    # Paso 3: Crear el asistente en Pinecone si no existe
    create_assistant_if_not_exists(api_key, assistant_name)
    
    # Paso 4: Listar y eliminar archivos existentes en Pinecone
    print("Listando archivos existentes en Pinecone para eliminarlos...")
    existing_files = list_files_in_pinecone(api_key, base_url)
    if isinstance(existing_files, list):
        for file_info in existing_files:
            file_id = file_info.get('id') if isinstance(file_info, dict) else file_info
            if file_id:
                print(f"Eliminando archivo con ID: {file_id}")
                delete_file_from_pinecone(api_key, base_url, file_id)
                time.sleep(5)
    else:
        print("La respuesta de la API no es una lista de IDs de archivos.")
    
    # Paso 5: Procesar todas las colecciones y subir los documentos a Pinecone
    process_collections(db, collection_names, data_dir, api_key, base_url)

    # Finalización
    print("Compilación, eliminación de archivos antiguos y subida de nuevos documentos completada.")

if __name__ == "__main__":
    main() # Re inicializacion de la base de datos vectorial
    #reinit_collection("Syllabus") # Para borrar y re subir la coleccion X a Pinecone con nuevos archivos. Se usara para los archivos cargados

# Nota: Este programa debe ejecutarse SOLO si se quiere reiniciar TODA la base de datos vectorial. 
# El reinicio tomará unos 30 segundos y no podrá realizar consultas a la base de datos vectorial durante ese tiempo.