import logging
from typing import Dict, List, Union, Optional, Any

from request_handler import RequestHandler
from cognito import CognitoAuth
from config_py import ENDPOINTS

logger = logging.getLogger(__name__)

class HabitTracker:
    def __init__(self):
        self.auth = CognitoAuth()
        self.request_handler = RequestHandler()
        self._temp_session = None  # Añadir para guardar la sesión temporal
        self._temp_username = None  # Añadir para guardar el usuario temporal

    def register(self, email: str) -> Dict:
        """Registra un nuevo usuario en el sistema."""
        logger.info(f"Intentando registrar usuario: {email}")
        return self.auth.register(email)

    def login(self, username: str, password: str) -> Dict:
        """Inicia sesión en el sistema."""
        logger.info(f"Intentando login para usuario: {username}")
        response = self.auth.login(username, password)

        # Guardar la sesión y username si se requiere cambio de contraseña
        if response.get('status') == 'NEW_PASSWORD_REQUIRED':
            self._temp_session = response.get('session')
            self._temp_username = username
            logger.info("Guardando sesión temporal para cambio de contraseña")

        if response['status'] == 'SUCCESS' and 'token' in response:
            self.request_handler.set_token(response['token'])
            self._temp_session = None  # Limpiar sesión temporal
            self._temp_username = None  # Limpiar username temporal

        return response

    def change_password(self, username: str, session: str, new_password: str) -> Dict:
        """Cambia la contraseña cuando es requerido."""
        try:
            # Si tenemos una sesión temporal guardada, usarla
            if self._temp_session and self._temp_username:
                logger.info("Usando sesión temporal guardada para cambio de contraseña")
                username = self._temp_username
                session = self._temp_session

            if not session:
                return {
                    "status": "ERROR",
                    "message": "Se requiere iniciar sesión primero con la contraseña temporal"
                }

            logger.info(f"Intentando cambiar contraseña para usuario: {username}")
            response = self.auth.change_password(username, session, new_password)

            if response['status'] == 'SUCCESS' and 'token' in response:
                self.request_handler.set_token(response['token'])
                self._temp_session = None  # Limpiar sesión temporal
                self._temp_username = None  # Limpiar username temporal

            return response
        except Exception as e:
            logger.error(f"Error durante el cambio de contraseña: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e)
            }

    def needs_password_change(self) -> bool:
        """Verifica si el usuario necesita cambiar su contraseña."""
        return bool(self._temp_session and self._temp_username)

    def logout(self) -> Dict:
        """Cierra la sesión actual."""
        logger.info("Cerrando sesión")
        self.request_handler.clear_token()
        return self.auth.logout()

    def add_habit(self, name: str, description: Optional[str] = None, frequency: str = "daily") -> Dict:
        """Añade un nuevo hábito."""
        logger.info(f"Añadiendo nuevo hábito: {name}")
        data = {
            "habit_name": name,
            "description": description,
            "frequency": frequency
        }
        return self.request_handler.post(ENDPOINTS['habits'], data)

    def get_habits(self) -> Union[List[Dict], Dict]:
        """Obtiene la lista de todos los hábitos."""
        logger.info("Obteniendo lista de hábitos")
        response = self.request_handler.get(ENDPOINTS['habits'])

        # Solo loggear la respuesta para debugging
        logger.debug(f"Respuesta completa de la API: {response}")

        formatted_response = self._format_habits_response(response)  # Formateamos la respuesta
        return formatted_response  # ¡Importante! Retornar la respuesta formateada

    def print_habits(self, habits: List[Dict]) -> None:
        """Imprime la lista de hábitos formateada."""
        if not habits:
            print("\nNo hay hábitos registrados.")
            return

        print("\n=== Lista de Hábitos ===")
        for habit in habits:
            print(f"\nHábito: {habit['name']}")
            print(f"  ID: {habit['id']}")
            if habit.get('description') and habit['description'] != 'Sin descripción':
                print(f"  Descripción: {habit['description']}")
            print(f"  Frecuencia: {habit['frequency']}")
            print(f"  Completado: {'Sí' if habit['completed'] else 'No'}")
            if habit['start_date']:
                print(f"  Fecha de inicio: {habit['start_date']}")
        print("=" * 20)

    def complete_habit(self, habit_id: str) -> Dict:
        """Marca un hábito como completado usando PUT."""
        if not habit_id:
            logger.warning("Intento de completar hábito sin ID")
            return {"status": "ERROR", "message": "El ID del hábito es requerido"}

        logger.info(f"Marcando hábito como completado: {habit_id}")

        # Primero obtenemos el hábito actual para mantener sus datos
        current_habits = self.get_habits()
        current_habit = next((h for h in current_habits if h['id'] == habit_id), None)

        if not current_habit:
            return {"status": "ERROR", "message": "Hábito no encontrado"}

        # Mostrar el estado actual y pedir confirmación
        print("\n" + "="*50)
        print(f"Hábito seleccionado: {current_habit['name']}")
        print(f"Estado actual:")
        print(f"- Completado: {'Sí' if current_habit.get('completed') else 'No'}")
        print(f"- Frecuencia: {current_habit.get('frequency', 'daily')}")
        print("="*50 + "\n")

        # Preguntar por cada campo que se puede actualizar
        updates = {}

        # Preguntar por el estado de completado
        completed = input("¿Marcar como completado? (s/n) [s]: ").lower() != 'n'
        updates['completed'] = completed

        # Preguntar por la frecuencia
        change_frequency = input("¿Desea cambiar la frecuencia? (s/n): ").lower() == 's'
        if change_frequency:
            while True:
                frequency = input("Nueva frecuencia (daily/weekly/monthly) [daily]: ").lower() or "daily"
                if frequency in ['daily', 'weekly', 'monthly']:
                    updates['frequency'] = frequency
                    break
                print("Frecuencia inválida. Use 'daily', 'weekly' o 'monthly'")

        # Construir los datos para la actualización
        data = {
            "habit_id": habit_id,
            "habit_name": current_habit['name'],  # Mantenemos el nombre actual
            **updates  # Añadimos las actualizaciones elegidas
        }

        # Mostrar resumen de la actualización
        print("\n" + "="*50)
        print("Datos que se enviarán:")
        print(f"- ID: {data['habit_id']}")
        print(f"- Nombre: {data['habit_name']}")
        print(f"- Completado: {'Sí' if data['completed'] else 'No'}")
        if 'frequency' in data:
            print(f"- Frecuencia: {data['frequency']}")
        print("="*50 + "\n")

        # Confirmar actualización
        if input("¿Confirmar actualización? (s/n) [s]: ").lower() == 'n':
            return {"status": "CANCELLED", "message": "Actualización cancelada por el usuario"}

        logger.debug(f"Enviando datos para actualizar: {data}")
        response = self.request_handler.put(ENDPOINTS['habits'], data)

        if response.get('status') != 'ERROR':
            print("\n" + "="*50)
            print("Actualización exitosa!")
            print(f"Mensaje: {response.get('message', 'Hábito actualizado correctamente')}")
            print("="*50 + "\n")

        return response

    def update_habit(self, habit_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza cualquier campo de un hábito."""
        if not habit_id:
            logger.warning("Intento de actualizar hábito sin ID")
            return {"status": "ERROR", "message": "El ID del hábito es requerido"}

        # Log para debugging
        logger.info(f"Recibiendo actualización para hábito {habit_id}")
        logger.info(f"Datos de actualización: {updates}")

        # Remover el habit_id de los updates si está presente
        updates_clean = updates.copy()
        updates_clean.pop('habit_id', None)

        # Primero obtenemos el hábito actual
        current_habits = self.get_habits()
        current_habit = next((h for h in current_habits if h['id'] == habit_id), None)

        if not current_habit:
            return {"status": "ERROR", "message": "Hábito no encontrado"}

        # Validar que solo se permitan campos válidos
        valid_fields = {'habit_name', 'frequency', 'completed', 'description'}
        invalid_fields = set(updates_clean.keys()) - valid_fields
        if invalid_fields:
            return {
                "status": "ERROR",
                "message": f"Campos inválidos: {', '.join(invalid_fields)}"
            }

        # Construir datos para actualización
        data = {
            "habit_id": habit_id,  # El ID se incluye pero no como parte de la actualización
            "habit_name": current_habit['name'],
            "description": current_habit.get('description', ''),
            "frequency": current_habit.get('frequency', 'daily'),
            "completed": current_habit.get('completed', False),
        }

        # Actualizar con los nuevos datos
        data.update(updates_clean)

        # Log para debugging
        logger.info(f"Enviando datos finales para actualización: {data}")

        return self.request_handler.put(ENDPOINTS['habits'], data)
    def delete_habit(self, habit_id: str) -> Dict:
        """Elimina un hábito específico."""
        if not habit_id:
            logger.warning("Intento de eliminar hábito sin ID")
            return {"status": "ERROR", "message": "El ID del hábito es requerido"}

        logger.info(f"Eliminando hábito: {habit_id}")

        try:
            # Enviamos solo el habit_id en el body
            data = {"habit_id": habit_id}
            response = self.request_handler.delete(ENDPOINTS['habits'], data)

            # Si la respuesta es exitosa pero no tiene un mensaje específico
            if isinstance(response, dict) and not response.get('message'):
                return {
                    "status": "SUCCESS",
                    "message": f"Hábito eliminado correctamente"
                }
            return response

        except Exception as e:
            logger.error(f"Error al eliminar hábito: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Error al eliminar el hábito: {str(e)}"
            }

    def _format_habits_response(self, response: Union[Dict, List]) -> List[Dict]:
        """Formatea la respuesta de hábitos para mantener consistencia."""
        try:
            # Imprimir la respuesta raw para debugging
            logger.debug(f"Respuesta raw recibida: {response}")

            # Extraer los hábitos de la respuesta
            if isinstance(response, dict):
                if response.get('status') == 'ERROR':
                    logger.error(f"Error en respuesta: {response.get('message')}")
                    return []
                habits = response.get('Items', []) or response.get('items', []) or response.get('habits', [])
            elif isinstance(response, list):
                habits = response
            else:
                habits = []

            formatted_habits = []
            for habit in habits:
                if not isinstance(habit, dict):
                    continue

                # Imprimir el hábito raw para debugging
                logger.debug(f"Hábito raw recibido: {habit}")

                # Manejar la descripción con más cuidado
                description = habit.get('description', '')
                if description is None or description == '':
                    description = 'Sin descripción'

                formatted_habit = {
                    'id': habit.get('habit_id', ''),
                    'name': habit.get('habit_name', 'Sin nombre'),
                    'description': description,
                    'frequency': habit.get('frequency', 'daily'),
                    'completed': habit.get('completed', False),
                    'start_date': habit.get('start_date', '')
                }

                # Imprimir el hábito formateado para debugging
                logger.debug(f"Hábito formateado: {formatted_habit}")

                formatted_habits.append(formatted_habit)

            return formatted_habits

        except Exception as e:
            logger.error(f"Error al formatear respuesta de hábitos: {str(e)}")
            return []

    @property
    def is_authenticated(self) -> bool:
        """Verifica si hay una sesión activa."""
        return self.request_handler.is_authenticated