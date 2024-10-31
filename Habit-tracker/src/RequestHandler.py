import requests
import json
from urllib.parse import urljoin
from config_py import API_URL, USER_POOL_ID, CLIENT_ID, REGION

class RequestHandler:
    """
    Manejador de peticiones HTTP con integración de configuración de AWS Cognito.
    """

    def __init__(self):
        """
        Inicializa el RequestHandler usando la configuración global.
        """
        self.api_url = API_URL
        self.user_pool_id = USER_POOL_ID
        self.client_id = CLIENT_ID
        self.region = REGION
        self.token = None
        self.session = requests.Session()

    def _make_request(self, method, endpoint, data=None):
        """
        Realiza peticiones HTTP manejando la autenticación con Cognito.

        Args:
            method (str): Método HTTP ('GET', 'POST', 'PUT', 'DELETE')
            endpoint (str): Endpoint de la API
            data (dict, optional): Datos para enviar en la petición

        Returns:
            dict: Respuesta de la API procesada
        """
        if not self.token and endpoint != 'login':
            return {"error": "No hay sesión iniciada"}

        # Construir la URL completa
        url = urljoin(self.api_url, endpoint)

        # Preparar los headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Añadir el token de autorización si existe
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            # Preparar la request
            request_kwargs = {
                'headers': headers,
                'url': url
            }

            if data is not None and method in ['POST', 'PUT']:
                request_kwargs['json'] = data

            # Hacer la request
            response = self.session.request(method, **request_kwargs)

            # Imprimir información de debug
            print(f"Request URL: {url}")
            print(f"Request headers: {headers}")
            print(f"Request data: {data}")
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")

            # Manejar casos específicos de respuesta
            if response.status_code == 401:
                self.clear_token()  # Limpiar el token si está expirado
                return {"error": "Sesión expirada. Por favor, inicia sesión nuevamente."}

            if response.status_code == 403:
                self.clear_token()  # Limpiar el token si no está autorizado
                return {"error": "Error de autorización. Por favor, inicia sesión nuevamente."}

            response.raise_for_status()

            # Procesar la respuesta
            try:
                json_response = response.json()

                # Manejar caso especial del login
                if endpoint == 'login' and 'token' in json_response:
                    self.token = json_response['token']

                # Manejar caso de cambio de contraseña requerido
                if 'message' in json_response and 'Se requiere cambiar la contraseña' in json_response['message']:
                    return {
                        "status": "NEW_PASSWORD_REQUIRED",
                        "session": json_response.get('session'),
                        "message": json_response['message']
                    }

                return json_response
            except json.JSONDecodeError:
                return {"message": response.text}

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "401" in error_msg:
                self.clear_token()  # Limpiar el token si hay error de autorización
                return {"error": "Error de autorización. Por favor, inicia sesión nuevamente."}
            return {"error": error_msg}

    def set_token(self, token):
        """
        Establece el token de autenticación y lo guarda en la sesión.

        Args:
            token (str): Token JWT de autenticación
        """
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def clear_token(self):
        """
        Limpia el token de autenticación y lo remueve de la sesión.
        """
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']

    @property
    def is_authenticated(self):
        """
        Verifica si hay una sesión activa.

        Returns:
            bool: True si hay un token válido, False en caso contrario
        """
        return self.token is not None