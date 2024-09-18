import uuid
from datetime import datetime


class HabitTracker:
    def __init__(self):
        self.habits = {}

    def add_habit(self, habit_name, frequency="diaria", start_date=None):
        if habit_name not in self.habits:
            habit_id = str(uuid.uuid4())  # Se genera un identifier único
            start_date = start_date or datetime.now().strftime('%Y-%m-%d')
            self.habits[habit_name] = {
                "id": habit_id,
                "frequency": frequency,
                "start_date": start_date,
                "completed": False
            }
            return f"Hábito '{habit_name}' añadido con ID {habit_id}"
        else:
            return f"El hábito '{habit_name}' ya existe"

    def complete_habit(self,habit_name):
        if habit_name in self.habits:
            self.habits[habit_name] = True
            return (f"Habito "
                    f"'{habit_name}' marcado como completado")
        else:
            return f"El habito '{habit_name}' no existe"

    def delete_habit(self,habit_name):
        if habit_name in self.habits:
            del self.habits[habit_name]
            return f"Habito '{habit_name}' eliminado"
        else:
            return f"El habito '{habit_name}' no existe"

    def list_habits(self):
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
