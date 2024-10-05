import requests
import os

# Obtener la URL desde la variable de entorno AUTH_SRV_URL, o usar 'http://localhost:2000' como valor por defecto
BASE_URL = os.getenv('AUTH_SRV_URL', 'http://localhost:2000')

# Función para verificar si un token JWT es válido
def is_token_valid(token):
    """
    Verifica si el token proporcionado es válido.
    
    :param token: El token JWT como cadena de texto.
    :return: True si el token es válido, False si no lo es.
    """
    headers = {
        'Authorization': f'Bearer {token}',  # Agregar "Bearer" antes del token
        'accept': 'application/json'
    }

    try:
        # Hacer la solicitud POST al endpoint /verify
        response = requests.post(f'{BASE_URL}/verify', headers=headers)
        
        # Si la respuesta es 200, el token es válido
        if response.status_code == 200:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        # En caso de error en la conexión o solicitud
        print(f"Error during request: {e}")
        return False


# Función para validar el encabezado de autorización y el token
def validate_auth_header(auth_header):
    """
    Valida el encabezado de autorización y el token.

    :param auth_header: El valor del encabezado de autorización ('Bearer <token>')
    :return: True si el token es válido, False si no.
    """
    # Verificar si el encabezado de autorización está presente y bien formado
    if not auth_header or not auth_header.startswith('Bearer '):
        return False

    # Extraer el token del encabezado
    token = auth_header.split(" ")[1]
    print(f"Token recibido: {token}")

    # Verificar si el token es válido
    return is_token_valid(token)


# Ejemplo de uso
if __name__ == '__main__':

    '''
    # Token válido
    example_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZF91c3VhcmlvIjoxLCJ1c3VhcmlvIjoiTHVpcyBCcmF2byIsImVtYWlsIjoibHVpcy5icmF2b0BqYXZlcmlhbmEuZWR1LmNvbSIsImlkX2NhdGVnb3JpYSI6MiwiaWF0IjoxNzI4MTA4ODIyLCJleHAiOjE3MjgxMTI0MjJ9.buFGZ9yxtycUY9WHTHmMdjDtSbLFVkNQtgxNbs5hBNsK4VPwTKB0TmizM9cm-JdBXWrdLIfAmxbMPZVPipkXdg"
    is_valid = is_token_valid(example_token)
    print(f"Token válido: {is_valid}")
    '''