import os
import json
import io
import requests
from pymongo import MongoClient
import time

# Paso 1: Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')

if not mongo_uri:
    print("URI de conexión no encontrada. Construyendo URI de conexión...")
    user = os.getenv('MONGO_USER', 'admin')
    password = os.getenv('MONGO_PASS', 'admin123')
    host = os.getenv('MONGO_HOST', 'localhost')
    mongo_uri = f"mongodb://{user}:{password}@{host}:27017"

# Inicializa el cliente MongoDB
client = MongoClient(mongo_uri)

# Bases de datos y colecciones a consultar
db = client['ALIE_DB']
collection_names = ["Syllabus", 
                    "InformacionPrivada_General", 
                    "InformacionPrivada_QA", 
                    "InformacionPublica_General", 
                    "InformacionPublica_QA"]

# Paso 2: Configurar las variables de Pinecone
api_key = os.getenv("PINECONE_API_KEY")  # Clave API de Pinecone desde las variables de entorno
assistant_name = os.getenv("ASSISTANT_NAME", "alie")  # Nombre del asistente
base_url = f"https://prod-1-data.ke.pinecone.io/assistant/files/{assistant_name}"

# Paso 3: Obtener el directorio del script actual y crear la carpeta "data" en ese lugar
current_dir = os.path.dirname(os.path.realpath(__file__))  # Obtiene la ruta del script actual
data_dir = os.path.join(current_dir, 'data')  # Crea la ruta hacia la carpeta "data"

# Crear la carpeta "data" si no existe
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Función para listar archivos en Pinecone
def list_files_in_pinecone():
    response = requests.get(base_url, headers={"Api-Key": api_key})
    
    if response.status_code == 200:
        files = response.json().get('files', [])
        print(f"Respuesta completa de la API: {files}")
        return files
    else:
        print(f"Error al listar archivos. Código de estado: {response.status_code}, Respuesta: {response.text}")
        return []

# Función para eliminar archivos en Pinecone
def delete_file_from_pinecone(file_id):
    delete_url = f"{base_url}/{file_id}"
    response = requests.delete(delete_url, headers={"Api-Key": api_key})
    
    if response.status_code == 200:
        print(f"Archivo {file_id} eliminado exitosamente.")
    else:
        print(f"Error al eliminar archivo {file_id}. Código de estado: {response.status_code}, Respuesta: {response.text}")

# Paso 4: Función para subir un archivo compilado de una colección a Pinecone
def upload_compiled_doc_to_pinecone(filepath, collection_name):
    # Leer el archivo para subirlo
    with open(filepath, 'r', encoding='utf-8') as file:
        temp_file = io.StringIO(file.read())
        temp_file.seek(0)  # Regresar el cursor al inicio del archivo en memoria
    
    # Subir el archivo compilado a Pinecone
    response = requests.post(
        base_url,
        headers={"Api-Key": api_key},
        files={"file": (f"{collection_name}_compiled.txt", temp_file)}
    )
    
    # Verificar la respuesta
    if response.status_code == 200:
        print(f"Archivo '{collection_name}_compiled.txt' subido exitosamente. Response: {response.text}")
    else:
        print(f"Error al subir archivo '{collection_name}_compiled.txt'. Código de estado: {response.status_code}, Respuesta: {response.text}")
    
    # Cerrar el archivo temporal en memoria
    temp_file.close()

# Paso 5: Eliminar todos los archivos en Pinecone antes de subir los nuevos
print("Listando archivos existentes en Pinecone para eliminarlos...")
existing_files = list_files_in_pinecone()

if isinstance(existing_files, list):  # Asegúrate de que es una lista
    for file_info in existing_files:
        # Dependiendo de la estructura de file_info, usa 'file_info' o 'file_info.get('id')'
        if isinstance(file_info, dict):
            file_id = file_info.get('id')
        else:
            file_id = file_info
        
        if file_id:
            print(f"Eliminando archivo con ID: {file_id}")
            delete_file_from_pinecone(file_id)
            time.sleep(2)  # Esperar entre solicitudes para evitar sobrecargar la API
else:
    print("La respuesta de la API no es una lista de IDs de archivos.")

# Paso 6: Procesar cada colección y compilar los documentos en un archivo
for collection_name in collection_names:
    collection = db[collection_name]
    documents = collection.find()
    
    # Nombre del archivo compilado
    compiled_filepath = os.path.join(data_dir, f"{collection_name}_compiled.txt")
    
    # Abrir el archivo compilado para escribir todos los documentos
    with open(compiled_filepath, 'w', encoding='utf-8') as compiled_file:
        for document in documents:
            # Escribir cada documento en el archivo
            compiled_file.write(json.dumps(document, ensure_ascii=False, default=str) + "\n")
    
    # Subir el archivo compilado a Pinecone
    upload_compiled_doc_to_pinecone(compiled_filepath, collection_name)
    time.sleep(2)  # Esperar entre solicitudes para evitar sobrecargar la API

print("Compilación, eliminación de archivos antiguos y subida de nuevos documentos completada.")


# Nota: Este programa debe ejecutarse SOLO si se quiere reiniciar TODA la base de datos vectorial. 
# El reinicio tomará unos 30 segundos y no podrá realizar consultas a la base de datos vectorial durante ese tiempo.