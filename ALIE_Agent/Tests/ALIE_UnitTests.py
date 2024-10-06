# pip install pytest requests

# To run: pytest ALIE_Agent\Tests\ALIE_UnitTests.py

import unittest
import requests

# Auth Headers
import requests

# Datos de autenticación
BASE_URL_AUTH = 'http://localhost:2001/api/auth'  # La URL de la API de autenticación
USERNAME = "luis.bravo@javeriana.edu.com"
PASSWORD = "123456"

def login_and_get_header():
    """
    Inicia sesión, obtiene el token de autenticación, y devuelve un encabezado de autorización.
    
    :return: dict - encabezado con el token de autorización y 'accept': 'application/json'
    """
    # Definir payload para iniciar sesión
    payload = {
        "email": USERNAME,
        "contrasena": PASSWORD
    }

    # Hacer la solicitud POST al endpoint /login
    response = requests.post(f'{BASE_URL_AUTH}/login', json=payload)

    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        # Extraer token de la respuesta
        response_data = response.json()
        token = response_data['token']
        print(f"Token obtenido: {token}")

        # Crear el header con el token y el campo 'accept'
        headers = {
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        }

        # Retornar el header para usarlo en otras solicitudes
        return headers
    else:
        # Si falla el login, imprimir el error y devolver None
        print(f"Error al iniciar sesión: {response.status_code} - {response.text}")
        return None

headers = {} # Encabezados de la solicitud. Vacío por ahora



# ALIE API

BASE_URL = 'http://localhost:3000/api/ia/chat'  # The live API URL

class ALIELiveEndpointTestCase(unittest.TestCase):
    
    def test_alie_success(self):
        # Define payload for the request
        payload = {
        "input": "Cual es el codigo de estructuras de datos?",
        "priority": "False"
        }

        # Make POST request to the live /tag endpoint
        response = requests.post(BASE_URL, json=payload, headers=headers)

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['answer'] is not None
        
    def test_alie_no_prompt(self):
        # Define payload for the request
        payload = {
        "priority": "False"
        }

        # Make POST request to the live /tag endpoint
        response = requests.post(BASE_URL, json=payload, headers=headers)

        # Assertions
        assert response.status_code == 400
        response_data = response.json()
        assert response_data['error'] == 'No prompt provided'

    def test_alie_success_failure(self):
        # Define payload for the request
        payload = {
        "input": "Cual es el codigo de estructuras de datos?",
        "priority": "False"
        }

        # Create a new header without the auth_token, but an invalid token
        invalid_token = "invalid_token"
        headers_specific = {
            'Authorization': f'Bearer {invalid_token}',  # Agregar "Bearer" antes del token
            'accept': 'application/json'
        }

        # Make POST request to the live /tag endpoint
        response = requests.post(BASE_URL, json=payload, headers=headers_specific)

        # Assertions - checking for failure (400 or 500)
        assert response.status_code == 401
        response_data = response.json()
        assert response_data['success'] is False
        assert 'Token de autorización inválido o faltante' in response_data['message']


if __name__ == '__main__':

    headers = login_and_get_header() # Get the auth header
    unittest.main()
