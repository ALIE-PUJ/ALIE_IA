import time
import requests
import os  # Importar el módulo os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

# Datos de autenticación
BASE_URL_AUTH = 'http://localhost:2001/api/auth'
USERNAME = "luis.bravo@javeriana.edu.com"
PASSWORD = "123456"

# ALIE API
BASE_URL = 'http://localhost:3000/api/ia/chat'

# Headers de la solicitud
headers = {}

# Payload de la solicitud
payload = {
    "input": "Cual es el codigo de estructuras de datos?",
    "priority": "False"
}

# Función para obtener el token de autorización
def login_and_get_header():
    payload = {
        "email": USERNAME,
        "contrasena": PASSWORD
    }
    response = requests.post(f'{BASE_URL_AUTH}/login', json=payload)
    if response.status_code == 200:
        token = response.json()['token']
        headers = {
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        }
        return headers
    else:
        print(f"Error al iniciar sesión: {response.status_code} - {response.text}")
        return None

# Función que envía una solicitud al API
def send_request(headers, start_event, request_number):
    start_event.wait()  # Espera a que todas las solicitudes estén listas para empezar

    start_time = time.time()
    response = requests.post(BASE_URL, json=payload, headers=headers)
    end_time = time.time()

    response_time = end_time - start_time
    response_data = response.json() if response.status_code == 200 else None
    
    # Obtener la respuesta del API
    answer = response_data.get('answer', 'No hay respuesta') if response.status_code == 200 else None

    # Verificar si hubo éxito considerando el contenido de 'answer'
    success = response.status_code == 200 and answer != "Estamos resolviendo algunos inconvenientes. Intenta de nuevo en unos minutos."

    result = {
        "request_number": request_number,
        "success": success,
        "status_code": response.status_code,
        "response_time": response_time,
        "response_data": response_data,
        "answer": answer
    }
    
    print(f"Solicitud #{request_number}: {result['success']} (Código: {result['status_code']}, Tiempo: {result['response_time']:.4f}s, Respuesta: {result['answer']})")
    return result

# Función principal para ejecutar la prueba de carga
def load_test(num_requests, concurrency):
    if headers is None:
        print("No se pudo obtener el token de autorización. Prueba abortada.")
        return

    response_times = []
    errors = 0
    results = []  # Almacenar los resultados de cada solicitud

    start_event = Event()  # Crear un evento que sincronizará los hilos

    # Ejecutar las solicitudes concurrentemente
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, headers, start_event, i + 1) for i in range(num_requests)]

        # Inicia todas las solicitudes al mismo tiempo
        start_event.set()

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["success"]:
                response_times.append(result["response_time"])
            else:
                errors += 1

    # Calcular estadísticas de las respuestas
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
    else:
        avg_response_time = max_response_time = min_response_time = 0

    # Obtener la ruta del directorio actual
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Guardar resultados en un archivo en el mismo directorio del script
    result_file_path = os.path.join(current_directory, 'ALIE_LoadTestsResults.txt')

    # Guardar los resultados en el archivo (solo resumen)
    with open(result_file_path, 'a', encoding='utf-8') as f:  # Especificar la codificación UTF-8 y modo append
        f.write(f"\nResultados de la prueba de carga con {num_requests} solicitudes y {concurrency} hilos:\n")
        f.write(f"Tiempos de respuesta: mínimo={min_response_time:.4f}s, máximo={max_response_time:.4f}s, promedio={avg_response_time:.4f}s\n")
        f.write(f"Solicitudes exitosas: {len(response_times)}\n")
        f.write(f"Solicitudes fallidas: {errors}\n")

    # Mostrar resultados de la prueba
    print(f"\nResultados de la prueba de carga con {num_requests} solicitudes y {concurrency} hilos:")
    print(f"Tiempos de respuesta: mínimo={min_response_time:.4f}s, máximo={max_response_time:.4f}s, promedio={avg_response_time:.4f}s")
    print(f"Solicitudes exitosas: {len(response_times)}")
    print(f"Solicitudes fallidas: {errors}")

# Ejecutar la prueba de carga con diferentes niveles de concurrencia
if __name__ == "__main__":
    # Inicializar los headers de la solicitud
    headers = login_and_get_header()

    num_requests = 100  # Número total de solicitudes a enviar, en total
    concurrency_levels = [1, 5, 10, 25, 50, 75, 100]  # Diferentes niveles de concurrencia

    # Limpiar el archivo antes de comenzar
    result_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ALIE_LoadTestsResults.txt')
    with open(result_file_path, 'w', encoding='utf-8') as f:  # Limpiar el archivo al inicio
        f.write("Resultados de las pruebas de carga:\n")

    for concurrency in concurrency_levels:
        load_test(num_requests, concurrency)


'''

Resultados para el computador de Luis 
(1 sola instancia de ALIE y LMStudio en ejecución. Tagging para todas las interacciones)
(Timeout: 60 segundos. Modelos: 2. LmStudio (ALIE-Model), Groq (Llama3-70b))

Resultados de las pruebas de carga:

Resultados de la prueba de carga con 100 solicitudes y 1 hilos:
Tiempos de respuesta: mínimo=2.4400s, máximo=2.8440s, promedio=2.5624s
Solicitudes exitosas: 100
Solicitudes fallidas: 0

Resultados de la prueba de carga con 100 solicitudes y 5 hilos:
Tiempos de respuesta: mínimo=4.1570s, máximo=11.1913s, promedio=10.3511s
Solicitudes exitosas: 100
Solicitudes fallidas: 0

Resultados de la prueba de carga con 100 solicitudes y 10 hilos:
Tiempos de respuesta: mínimo=6.9310s, máximo=21.2459s, promedio=19.6954s
Solicitudes exitosas: 100
Solicitudes fallidas: 0

Resultados de la prueba de carga con 100 solicitudes y 25 hilos:
Tiempos de respuesta: mínimo=14.9746s, máximo=52.2312s, promedio=44.5099s
Solicitudes exitosas: 100
Solicitudes fallidas: 0

Resultados de la prueba de carga con 100 solicitudes y 50 hilos:
Tiempos de respuesta: mínimo=30.2309s, máximo=62.5597s, promedio=48.7059s
Solicitudes exitosas: 63
Solicitudes fallidas: 37

Resultados de la prueba de carga con 100 solicitudes y 75 hilos:
Tiempos de respuesta: mínimo=0.0000s, máximo=0.0000s, promedio=0.0000s
Solicitudes exitosas: 0
Solicitudes fallidas: 100

Resultados de la prueba de carga con 100 solicitudes y 100 hilos:
Tiempos de respuesta: mínimo=0.0000s, máximo=0.0000s, promedio=0.0000s
Solicitudes exitosas: 0
Solicitudes fallidas: 100

'''