# habit_tracker.py
import uuid
from datetime import datetime
import boto3
from warrant import Cognito
import requests
import config_py


class HabitTracker:
    def __init__(self):
        self.habits = {}
        self.cognito_user = None
        self.token = None
        self.user_id = None

    def _make_request(self, method, endpoint, data=None):
        #Método auxiliar para hacer peticiones a la API
        if not self.token:
            return {"error": "No hay sesión iniciada"}

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        url = f"{config_py.API_URL}/{endpoint}"
        print(f"Making request to: {url}")  # Para debugging

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)

            print(f"Response status: {response.status_code}")  # Para debugging
            print(f"Response content: {response.text}")  # Para debugging

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def add_habit(self, habit_name, frequency="diaria", start_date=None):
        if not self.token:
            return "Debes iniciar sesión primero"

        start_date = start_date or datetime.now().strftime('%Y-%m-%d')
        habit_data = {
            "habit_name": habit_name,
            "frequency": frequency,
            "start_date": start_date,
            "user_id": self.user_id,
            "completed": False
        }

        response = self._make_request('POST', 'habits', habit_data)
        if 'error' in response:
            return f"Error al añadir el hábito: {response['error']}"

        habit_id = response.get('habitId', str(uuid.uuid4()))
        self.habits[habit_name] = {
            "id": habit_id,
            "frequency": frequency,
            "start_date": start_date,
            "completed": False
        }

        return f"Hábito '{habit_name}' añadido con ID {habit_id}"

    def complete_habit(self, habit_name):
        if not self.token:
            return "Debes iniciar sesión primero"

        if habit_name not in self.habits:
            return f"El hábito '{habit_name}' no existe"

        habit_id = self.habits[habit_name]['id']
        data = {
            "habit_id": habit_id,
            "user_id": self.user_id,
            "completed": True
        }

        response = self._make_request('PUT', f'habits/{habit_id}', data)
        if 'error' in response:
            return f"Error al completar el hábito: {response['error']}"

        self.habits[habit_name]['completed'] = True
        return f"Hábito '{habit_name}' marcado como completado"

    def delete_habit(self, habit_name):
        if not self.token:
            return "Debes iniciar sesión primero"

        if habit_name not in self.habits:
            return f"El hábito '{habit_name}' no existe"

        habit_id = self.habits[habit_name]['id']
        response = self._make_request('DELETE', f'habits/{habit_id}')

        if 'error' in response:
            return f"Error al eliminar el hábito: {response['error']}"

        del self.habits[habit_name]
        return f"Hábito '{habit_name}' eliminado"

    def list_habits(self):
        if not self.token:
            return "Debes iniciar sesión primero"

        response = self._make_request('GET', f'habits')  # Endpoint modificado

        if 'error' in response:
            return f"Error al obtener los hábitos: {response['error']}"

        habits_data = response.get('Items', [])  # Cambiado a 'Items' según el formato de DynamoDB

        # Actualizar el almacenamiento local con los datos del servidor
        self.habits = {}
        for habit in habits_data:
            if habit.get('user_id') == self.user_id:  # Filtrar solo los hábitos del usuario actual
                self.habits[habit['habit_name']] = {
                    "id": habit['habit_id'],
                    "frequency": habit.get('frequency', 'diaria'),
                    "start_date": habit.get('start_date', ''),
                    "completed": habit.get('completed', False)
                }

        if not self.habits:
            return "No hay hábitos registrados"

        habit_list = []
        for habit_name, details in self.habits.items():
            status = "Completado" if details['completed'] else "No completado"
            habit_info = (f"Hábito: {habit_name}\n"
                          f"ID: {details['id']}\n"
                          f"Frecuencia: {details['frequency']}\n"
                          f"Fecha de inicio: {details['start_date']}\n"
                          f"Estado: {status}\n")
            habit_list.append(habit_info)

        return "\n".join(habit_list)

    def register_user(self, email, password):
        cognito_client = boto3.client('cognito-idp', region_name=config_py.REGION)
        try:
            response = cognito_client.sign_up(
                ClientId=config_py.CLIENT_ID,
                Username=email,
                Password=password,
            )
            return response['UserSub']
        except Exception as e:
            return f"Error al registrar usuario: {e}"

    def login_user(self, email, password):
        try:
            self.cognito_user = Cognito(
                config_py.USER_POOL_ID,
                config_py.CLIENT_ID,
                username=email
            )
            self.cognito_user.authenticate(password=password)
            self.token = self.cognito_user.id_token
            self.user_id = self.cognito_user.sub

            # Cargar hábitos del usuario después del login
            self.list_habits()

            return self.token
        except Exception as e:
            return f"Error al iniciar sesión: {e}"