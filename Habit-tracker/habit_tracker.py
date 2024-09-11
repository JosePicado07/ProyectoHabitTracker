class HabitTracker:
    def __init__(self):
        self.habits = {}

    def add_habit(self,habit_name):
        if habit_name not in self.habits:
            self.habits[habit_name] = False
            return f"Habito '{habit_name}' anadido"
        else:
            return f"El habito '{habit_name}' ya existe"

    def complete_habit(self,habit_name):
        if habit_name in self.habits:
            self.habits[habit_name] = True
            return f"Habito '{habit_name}' marcado como completado"
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
            return "No hay habitos registrados"
        return "\n".join(f"{habit}: {'Completado' if status else 'No completado'}" for habit, status in self.habits.items())
