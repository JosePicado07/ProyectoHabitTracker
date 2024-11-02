from datetime import datetime
from RequestHandler import RequestHandler


class HabitTracker:
    def __init__(self):
        self.request_handler = RequestHandler()
    def register(self, email):
        """
        Registra un nuevo usuario en el sistema.
        Solo requiere email, la contraseña temporal será generada y enviada por correo.

        Args:
            email (str): Correo electrónico del usuario

        Returns:
            dict: Respuesta del servidor con el estado del registro
        """
        data = {
            "email": email
        }
        response = self.request_handler._make_request('POST', 'register', data)

        # Verificar si el registro fue exitoso
        if response.get('status') == 'SUCCESS':
            return {
                "status": "SUCCESS",
                "message": "Se ha enviado un correo con las instrucciones para completar el registro"
            }

        return response
    def change_password(self, username, session, new_password):
        """
        Cambia la contraseña cuando es requerido por Cognito.
        """
        data = {
            "username": username,
            "session": session,
            "new_password": new_password
        }
        return self.request_handler._make_request('POST', 'changepassword', data)

    def login(self, username, password):
        """
        Inicia sesión en el sistema.
        """
        data = {
            "username": username,  # Usa username en lugar de email para coincidir con la API
            "password": password
        }
        response = self.request_handler._make_request('POST', 'login', data)

        # Manejar la respuesta según su estado
        if response.get('status') == 'NEW_PASSWORD_REQUIRED':
            return {
                "status": "NEW_PASSWORD_REQUIRED",
                "session": response.get('session'),
                "message": "Se requiere cambiar la contraseña"
            }
        elif response.get('status') == 'SUCCESS':
            return {
                "status": "SUCCESS",
                "token": response.get('token')
            }
        else:
            return response

    def logout(self):
        """
        Cierra la sesión actual.
        """
        self.request_handler.clear_token()
        return {"message": "Sesión cerrada exitosamente"}

    def add_habit(self, name, description=None, frequency="daily"):
        """
        Añade un nuevo hábito.
        """
        data = {
            "name": name,
            "description": description,
            "frequency": frequency
        }
        return self.request_handler._make_request('POST', 'habits', data)

    def get_habits(self):
        """
        Obtiene la lista de todos los hábitos.
        """
        response = self.request_handler._make_request('GET', 'habits')

        # Imprimir la respuesta completa para debugging
        print("Respuesta completa de get_habits:", response)

        # Verificar si la respuesta es una lista o está dentro de alguna clave
        if isinstance(response, dict):
            # Si la respuesta es un diccionario, buscar la lista de hábitos
            habits = response.get('items', [])  # Intenta con 'items' primero
            if not habits:
                habits = response.get('habits', [])  # Intenta con 'habits' si 'items' no existe
            if not habits:
                # Si no encontramos la lista en ninguna clave conocida, devolver la respuesta completa
                habits = []
        elif isinstance(response, list):
            # Si la respuesta ya es una lista, usarla directamente
            habits = response
        else:
            # Si no es ni diccionario ni lista, devolver lista vacía
            habits = []

        # Verificar que cada hábito tenga los campos requeridos y mapear los nombres de campos
        validated_habits = []
        for habit in habits:
            if isinstance(habit, dict):
                validated_habit = {
                    'name': habit.get('habit_name', 'Sin nombre'),
                    'description': habit.get('description', 'Sin descripción'),
                    'frequency': habit.get('frequency', 'daily'),
                    'id': habit.get('habit_id', ''),
                    'completed': habit.get('completed', False),
                    'start_date': habit.get('start_date', '')
                }
                validated_habits.append(validated_habit)

        return validated_habits

    def update_habit(self, habit_id, updates):
        """
        Actualiza un hábito existente.
        """
        return self.request_handler._make_request('PUT', f'habits/{habit_id}', updates)

    def delete_habit(self, habit_id):
        """
        Elimina un hábito específico.
        """
        return self.request_handler._make_request('DELETE', f'habits/{habit_id}')

    def complete_habit(self, habit_id):
        """
        Marca un hábito como completado para el día actual.
        """
        if not habit_id:
            return {"error": "ID de hábito no válido"}
        data = {
            "completed_at": datetime.now().isoformat()
        }
        return self.request_handler._make_request(
            'POST',
            f'habits/{habit_id}/complete',
            data
        )

    def get_habit_history(self, habit_id):
        """
        Obtiene el historial de completado de un hábito específico.
        """
        return self.request_handler._make_request('GET', f'habits/{habit_id}/history')

    @property
    def is_authenticated(self):
        """
        Verifica si hay una sesión activa.
        """
        return self.request_handler.is_authenticated