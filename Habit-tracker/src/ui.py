import tkinter as tk
from tkinter import messagebox
from habit_tracker import HabitTracker


class HabitTrackerUI:
    def __init__(self, root):
        self.root = root
        self.tracker = HabitTracker()
        self.root.title("Habit Tracker")

        # Crear las secciones de la interfaz
        self.create_auth_section()
        self.create_habit_section()

    def create_auth_section(self):
        # Sección de autenticación
        auth_frame = tk.LabelFrame(self.root, text="Autenticación")
        auth_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        tk.Label(auth_frame, text="Email:").grid(row=0, column=0)
        self.email_entry = tk.Entry(auth_frame)
        self.email_entry.grid(row=0, column=1)

        tk.Label(auth_frame, text="Contraseña:").grid(row=1, column=0)
        self.password_entry = tk.Entry(auth_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(auth_frame, text="Registrarse", command=self.register_user).grid(row=2, column=0, pady=5)
        tk.Button(auth_frame, text="Iniciar sesión", command=self.login_user).grid(row=2, column=1, pady=5)

    def create_habit_section(self):
        # Sección de manejo de hábitos
        habit_frame = tk.LabelFrame(self.root, text="Gestión de Hábitos")
        habit_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        tk.Label(habit_frame, text="Nombre del Hábito:").grid(row=0, column=0)
        self.habit_name_entry = tk.Entry(habit_frame)
        self.habit_name_entry.grid(row=0, column=1)

        tk.Button(habit_frame, text="Añadir Hábito", command=self.add_habit).grid(row=1, column=0, pady=5)
        tk.Button(habit_frame, text="Completar Hábito", command=self.complete_habit).grid(row=1, column=1, pady=5)
        tk.Button(habit_frame, text="Eliminar Hábito", command=self.delete_habit).grid(row=1, column=2, pady=5)
        tk.Button(habit_frame, text="Listar Hábitos", command=self.list_habits).grid(row=2, column=0, columnspan=3,
                                                                                     pady=5)

    def register_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        result = self.tracker.register_user(email, password)
        messagebox.showinfo("Registro", result)

    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        result = self.tracker.login_user(email, password)
        if "Error" in result:
            messagebox.showerror("Error de Inicio de Sesión", result)
        else:
            messagebox.showinfo("Inicio de Sesión", "Inicio de sesión exitoso.")

    def add_habit(self):
        habit_name = self.habit_name_entry.get()
        result = self.tracker.add_habit(habit_name)
        messagebox.showinfo("Añadir Hábito", result)

    def complete_habit(self):
        habit_name = self.habit_name_entry.get()
        result = self.tracker.complete_habit(habit_name)
        messagebox.showinfo("Completar Hábito", result)

    def delete_habit(self):
        habit_name = self.habit_name_entry.get()
        result = self.tracker.delete_habit(habit_name)
        messagebox.showinfo("Eliminar Hábito", result)

    def list_habits(self):
        habits = self.tracker.list_habits()
        messagebox.showinfo("Lista de Hábitos", habits)


# Crear la aplicación de Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerUI(root)
    root.mainloop()
