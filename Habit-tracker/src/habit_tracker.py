from datetime import datetime
from RequestHandler import RequestHandler
class HabitTracker:
    class HabitTracker:
        def __init__(self):
            """
            Inicializa el HabitTracker utilizando el RequestHandler configurado.
            """
            self.request_handler = RequestHandler()

        def register(self, email, password):
            """
            Registra un nuevo usuario en el sistema.
            """
            data = {
                "email": email,
                "password": password
            }
            return self.request_handler._make_request('POST', 'register', data)

        def change_password(self, email, session, new_password):
            """
            Cambia la contraseña cuando es requerido por Cognito.
            """
            data = {
                "email": email,
                "session": session,
                "new_password": new_password
            }
            response = self.request_handler._make_request('POST', 'change-password', data)
            return response

        def login(self, email, password):
            """
            Inicia sesión en el sistema.
            """
            data = {
                "email": email,
                "password": password
            }
            return self.request_handler._make_request('POST', 'login', data)

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
            return self.request_handler._make_request('GET', 'habits')

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
            data = {
                "completed_at": datetime.now().isoformat()
            }
            return self.request_handler._make_request('POST', f'habits/{habit_id}/complete', data)

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