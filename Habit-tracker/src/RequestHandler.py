from urllib.parse import urlparse
import requests
import json
import datetime
import hmac
import hashlib
import base64
from config_py import API_URL, USER_POOL_ID, CLIENT_ID, REGION

class RequestHandler:
    def __init__(self):
        self.api_url = API_URL.rstrip('/')
        self.user_pool_id = USER_POOL_ID
        self.client_id = CLIENT_ID
        self.region = REGION
        self.token = None
        self.session = requests.Session()

    def _get_aws_auth_headers(self, method, endpoint, data=None):
        """
        Genera los headers necesarios para la autenticación con Bearer token
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }

        if self.token:
            # Imprimir el token para debugging
            print("Token actual:", self.token[:30] + "..." if self.token else "No hay token")

            # Asegurarse de que el token no tenga espacios extras o caracteres problemáticos
            cleaned_token = self.token.strip()
            headers['Authorization'] = f'Bearer {cleaned_token}'

            # Imprimir el header de autorización completo
            print("Header de autorización:", headers['Authorization'])
        else:
            print("No hay token disponible para la petición")

        return headers

    def _make_request(self, method, endpoint, data=None):
        endpoint = endpoint.strip('/')
        url = f"{self.api_url}/dev/{endpoint}"

        # Verificar autenticación antes de hacer la petición
        if not self.is_authenticated and endpoint not in ['login', 'register', 'changepassword']:
            print("No hay sesión activa")
            return {"error": "No hay sesión activa. Por favor, inicie sesión."}

        # Obtener headers
        headers = self._get_aws_auth_headers(method, endpoint, data)

        try:
            # Preparar los argumentos de la petición
            request_kwargs = {
                'headers': headers,
                'url': url
            }

            if data is not None and method in ['POST', 'PUT', 'DELETE']:
                request_kwargs['json'] = data

            # Debug info detallado
            print("\n=== Detalles de la petición ===")
            print(f"URL: {url}")
            print(f"Método: {method}")
            print("Headers:")
            for key, value in headers.items():
                print(f"  {key}: {value if key != 'Authorization' else value[:30] + '...'}")
            print(f"Datos: {json.dumps(data) if data else None}")
            print("===============================\n")

            # Realizar la petición
            response = self.session.request(method, **request_kwargs)

            print("\n=== Detalles de la respuesta ===")
            print(f"Status: {response.status_code}")
            print(f"Contenido: {response.text}")
            print("===============================\n")

            # Manejar errores de autenticación
            if response.status_code in [401, 403]:
                error_message = "Sesión expirada o token inválido. Por favor, inicie sesión nuevamente."
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_message = error_data['message']
                except:
                    pass

                print("Error de autenticación detectado. Limpiando token...")
                self.clear_token()
                return {
                    "error": error_message,
                    "status_code": response.status_code
                }

            try:
                json_response = response.json()

                # Manejo especial para login
                if endpoint == 'login':
                    if 'token' in json_response:
                        print("Token recibido en login. Estableciendo...")
                        self.set_token(json_response['token'])
                    elif json_response.get('message') == 'Se requiere cambiar la contraseña':
                        return {
                            "status": "NEW_PASSWORD_REQUIRED",
                            "session": json_response.get('session'),
                            "message": json_response.get('message')
                        }

                return json_response

            except json.JSONDecodeError:
                if response.status_code == 200:
                    return {"message": response.text}
                return {"error": "Error al procesar la respuesta del servidor"}

        except requests.exceptions.RequestException as e:
            print(f"Error en la petición: {str(e)}")
            return {"error": f"Error de conexión: {str(e)}"}

    def set_token(self, token):
        """
        Establece el token de autenticación JWT
        """
        if token:
            self.token = token.strip()
            print("Token establecido correctamente")
            print("Primeros 30 caracteres del token:", self.token[:30] + "...")
        else:
            print("Advertencia: Intento de establecer un token vacío")

    def clear_token(self):
        """
        Limpia el token de autenticación
        """
        self.token = None
        print("Token limpiado")

    @property
    def is_authenticated(self):
        """
        Verifica si hay una sesión activa
        """
        is_auth = self.token is not None
        print(f"Estado de autenticación: {'Autenticado' if is_auth else 'No autenticado'}")
        return is_auth

    def complete_habit(self, habit_id):
        """
        Marca un hábito como completado
        """
        if not habit_id:
            return {"error": "El ID del hábito es requerido"}

        print(f"Intentando completar hábito con ID: {habit_id}")
        return self._make_request('POST', f'habits/{habit_id}/complete', {})

    def delete_habit(self, habit_id):
        """
        Elimina un hábito
        """
        if not habit_id:
            return {"error": "El ID del hábito es requerido"}

        print(f"Intentando eliminar hábito con ID: {habit_id}")
        return self._make_request('DELETE', f'habits/{habit_id}')

    def get_habit_history(self, habit_id):
        """
        Obtiene el historial de un hábito
        """
        if not habit_id:
            return {"error": "El ID del hábito es requerido"}

        print(f"Obteniendo historial del hábito con ID: {habit_id}")
        return self._make_request('GET', f'habits/{habit_id}/history')