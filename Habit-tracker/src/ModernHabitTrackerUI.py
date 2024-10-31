import tkinter as tk
from ttkbootstrap import Style, ttk
from tkinter import messagebox
from habit_tracker import HabitTracker
import ttkbootstrap as tb


class ModernHabitTrackerUI:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme="flatly")
        self.tracker = HabitTracker()
        self.root.title("Habit Tracker")
        self.root.geometry("800x600")

        # Contenedor principal
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear las pestañas
        self.auth_frame = ttk.Frame(self.notebook, padding="20")
        self.habits_frame = ttk.Frame(self.notebook, padding="20")

        self.notebook.add(self.auth_frame, text="Autenticación")
        self.notebook.add(self.habits_frame, text="Hábitos")

        self.create_auth_section()
        self.create_habit_section()

        # Variables para mensajes de estado
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.main_container,
            textvariable=self.status_var,
            padding="10"
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def create_auth_section(self):
        # Título
        title_label = ttk.Label(
            self.auth_frame,
            text="Bienvenido a Habit Tracker",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=20)

        # Marco para el formulario
        form_frame = ttk.Frame(self.auth_frame)
        form_frame.pack(fill=tk.BOTH, padx=50)

        # Email
        ttk.Label(form_frame, text="Email:").pack(fill=tk.X, pady=(10, 0))
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.pack(fill=tk.X, pady=(0, 10))

        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").pack(fill=tk.X, pady=(10, 0))
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))

        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Registrarse",
            style="secondary.TButton",
            command=self.register_user
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Iniciar sesión",
            style="primary.TButton",
            command=self.login_user
        ).pack(side=tk.LEFT, padx=5)

    def create_habit_section(self):
        # Panel superior para añadir hábitos
        input_frame = ttk.Frame(self.habits_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(input_frame, text="Nombre del Hábito:").pack(side=tk.LEFT, padx=(0, 10))
        self.habit_name_entry = ttk.Entry(input_frame, width=40)
        self.habit_name_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            input_frame,
            text="Añadir Hábito",
            style="primary.TButton",
            command=self.add_habit
        ).pack(side=tk.LEFT)

        # Lista de hábitos
        self.habits_tree = ttk.Treeview(
            self.habits_frame,
            columns=("Nombre", "Estado"),
            show="headings"
        )
        self.habits_tree.heading("Nombre", text="Nombre")
        self.habits_tree.heading("Estado", text="Estado")
        self.habits_tree.pack(fill=tk.BOTH, expand=True)

        # Marco para botones de acción
        action_frame = ttk.Frame(self.habits_frame)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            action_frame,
            text="Completar Hábito",
            style="success.TButton",
            command=self.complete_habit
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Eliminar Hábito",
            style="danger.TButton",
            command=self.delete_habit
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Actualizar Lista",
            style="info.TButton",
            command=self.update_habit_list
        ).pack(side=tk.LEFT, padx=5)

    def update_habit_list(self):
        # Limpiar lista actual
        for item in self.habits_tree.get_children():
            self.habits_tree.delete(item)

        # Obtener y mostrar hábitos
        habits = self.tracker.list_habits()
        if isinstance(habits, str):  # Si es un mensaje de error
            self.status_var.set(habits)
            return

        for habit in habits:
            estado = "Completado" if habit.get('completed', False) else "Pendiente"
            self.habits_tree.insert("", tk.END, values=(habit['name'], estado))

    def register_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        result = self.tracker.register_user(email, password)
        self.status_var.set(result)
        if "Error" not in result:
            self.notebook.select(1)  # Cambiar a la pestaña de hábitos

    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        result = self.tracker.login_user(email, password)
        self.status_var.set(result)
        if "Error" not in result:
            self.notebook.select(1)  # Cambiar a la pestaña de hábitos
            self.update_habit_list()

    def add_habit(self):
        habit_name = self.habit_name_entry.get()
        result = self.tracker.add_habit(habit_name)
        self.status_var.set(result)
        self.habit_name_entry.delete(0, tk.END)
        self.update_habit_list()

    def complete_habit(self):
        selection = self.habits_tree.selection()
        if not selection:
            self.status_var.set("Por favor, selecciona un hábito")
            return

        habit_name = self.habits_tree.item(selection[0])['values'][0]
        result = self.tracker.complete_habit(habit_name)
        self.status_var.set(result)
        self.update_habit_list()

    def delete_habit(self):
        selection = self.habits_tree.selection()
        if not selection:
            self.status_var.set("Por favor, selecciona un hábito")
            return

        habit_name = self.habits_tree.item(selection[0])['values'][0]
        result = self.tracker.delete_habit(habit_name)
        self.status_var.set(result)
        self.update_habit_list()


if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = ModernHabitTrackerUI(root)
    root.mainloop()