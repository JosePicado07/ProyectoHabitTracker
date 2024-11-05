import logging
from typing import Dict, Any, Optional

import requests

from config_py import API_URL, USER_POOL_ID, CLIENT_ID, REGION


class RequestHandler:
    def __init__(self):
        self.api_url = API_URL.rstrip('/')
        self.user_pool_id = USER_POOL_ID
        self.client_id = CLIENT_ID
        self.region = REGION
        self.token = None
        self.session = requests.Session()

        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def set_token(self, token: str) -> None:
        """Establece el token de autenticación."""
        if not token or not isinstance(token, str):
            self.logger.warning("Intento de establecer un token inválido")
            raise ValueError("El token no puede estar vacío y debe ser una cadena de texto")

        self.token = token.strip()
        self.logger.info("Token establecido correctamente")

    def clear_token(self) -> None:
        """Limpia el token de autenticación."""
        self.token = None
        self.logger.info("Token limpiado")

    @property
    def is_authenticated(self) -> bool:
        """Verifica si hay un token de autenticación válido."""
        return bool(self.token)

    def _get_headers(self) -> Dict[str, str]:
        """Construye los headers para las peticiones HTTP."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        return headers

    def _validate_endpoint(self, endpoint: str) -> str:
        """Valida y formatea el endpoint."""
        if not endpoint:
            raise ValueError("El endpoint no puede estar vacío")

        # Eliminar slashes al inicio y final
        endpoint = endpoint.strip('/')
        return f"{self.api_url}/{endpoint}"

    def _make_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Realiza la petición HTTP con manejo de errores.
        """
        try:
            url = self._validate_endpoint(endpoint)
            headers = self._get_headers()

            self.logger.info(f"Realizando petición {method} a {url}")
            if data:
                self.logger.info(f"Datos enviados: {data}")  # Cambiado a INFO para ver siempre los datos

            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=30
            )

            try:
                response_data = response.json()
                self.logger.info(f"Respuesta recibida: {response_data}")  # Logging de la respuesta
            except ValueError:
                response_data = {"message": response.text}
                self.logger.warning(f"Respuesta no JSON: {response.text}")

            if not response.ok:
                self.logger.error(f"Error HTTP {response.status_code}: {response.text}")
                return {
                    "status": "ERROR",
                    "message": response_data.get('message', 'Error en la petición'),
                    "code": response.status_code
                }

            return response_data

        except requests.exceptions.ConnectionError:
            self.logger.error("Error de conexión")
            return {
                "status": "ERROR",
                "message": "Error de conexión. Verifica tu conexión a internet."
            }
        except requests.exceptions.Timeout:
            self.logger.error("Timeout en la petición")
            return {
                "status": "ERROR",
                "message": "La petición ha excedido el tiempo de espera."
            }
        except Exception as e:
            self.logger.error(f"Error inesperado: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e)
            }

    def get(self, endpoint: str) -> Dict[str, Any]:
        """Realiza una petición GET."""
        return self._make_request('GET', endpoint)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición POST."""
        return self._make_request('POST', endpoint, data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición PUT."""
        return self._make_request('PUT', endpoint, data)

    def delete(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Realiza una petición DELETE.
        Ahora acepta un parámetro data opcional para enviar en el body.
        """
        return self._make_request('DELETE', endpoint, data)