import tkinter as tk
from ttkbootstrap import Style, ttk
import ttkbootstrap as tb
from habit_tracker import HabitTracker
from tkinter import messagebox

# Constantes para traducciones
FREQUENCY_MAP = {
    'daily': 'diaria',
    'weekly': 'semanal',
    'monthly': 'mensual'
}

FREQUENCY_MAP_REVERSE = {
    'diaria': 'daily',
    'semanal': 'weekly',
    'mensual': 'monthly'
}

FREQUENCY_OPTIONS = ["diaria", "semanal", "mensual"]

PASSWORD_REQUIREMENTS = """
La contraseña debe contener:
- Al menos 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial
"""
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

        # Create notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear frames
        self.auth_frame = ttk.Frame(self.notebook, padding="20")
        self.habits_frame = ttk.Frame(self.notebook, padding="20")

        self.notebook.add(self.auth_frame, text="Autenticación")
        self.notebook.add(self.habits_frame, text="Hábitos")

        # Estado y mensajes
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.main_container,
            textvariable=self.status_var,
            padding="10"
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

        self.create_auth_section()
        self.create_habit_section()

        # Deshabilitar pestaña de hábitos hasta login
        self.notebook.tab(1, state="disabled")

    def create_auth_section(self):
        # Frame para autenticación
        auth_form = ttk.Frame(self.auth_frame)
        auth_form.pack(expand=True, fill=tk.BOTH, padx=50)

        # Campos
        ttk.Label(auth_form, text="Email:").pack(fill=tk.X, pady=(10, 0))
        self.email_entry = ttk.Entry(auth_form)
        self.email_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(auth_form, text="Contraseña:").pack(fill=tk.X, pady=(10, 0))
        self.password_entry = ttk.Entry(auth_form, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))

        # Botones
        btn_frame = ttk.Frame(auth_form)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="Registrarse",
            style="secondary.TButton",
            command=self.register_user
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Iniciar sesión",
            style="primary.TButton",
            command=self.login_user
        ).pack(side=tk.LEFT, padx=5)

        # Botón para cambiar contraseña
        ttk.Button(
            auth_form,
            text="Cambiar Contraseña",
            style="info.TButton",
            command=self.show_change_password_dialog
        ).pack(pady=10)

    def show_change_password_dialog(self):
        """Muestra un diálogo para cambiar la contraseña."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Contraseña")
        dialog.geometry("400x500")
        dialog.grab_set()  # Hace la ventana modal

        # Mostrar requisitos
        req_frame = ttk.LabelFrame(dialog, text="Requisitos", padding="10")
        req_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        ttk.Label(req_frame, text=PASSWORD_REQUIREMENTS, justify=tk.LEFT).pack()

        # Formulario
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.X, padx=20)

        ttk.Label(form_frame, text="Email:").pack(fill=tk.X)
        email_entry = ttk.Entry(form_frame)
        email_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Contraseña Actual:").pack(fill=tk.X)
        current_pass_entry = ttk.Entry(form_frame, show="*")
        current_pass_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Nueva Contraseña:").pack(fill=tk.X)
        new_pass_entry = ttk.Entry(form_frame, show="*")
        new_pass_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Confirmar Nueva Contraseña:").pack(fill=tk.X)
        confirm_pass_entry = ttk.Entry(form_frame, show="*")
        confirm_pass_entry.pack(fill=tk.X, pady=(0, 10))

        def handle_change():
            email = email_entry.get().strip()
            current_password = current_pass_entry.get()
            new_password = new_pass_entry.get()
            confirm_password = confirm_pass_entry.get()

            if not all([email, current_password, new_password, confirm_password]):
                self.set_status("❌ Todos los campos son requeridos", True)
                return

            if new_password != confirm_password:
                self.set_status("❌ Las contraseñas no coinciden", True)
                return

            # Si hay un cambio de contraseña pendiente
            if self.tracker.needs_password_change():
                response = self.tracker.change_password(None, None, new_password)
            else:
                login_response = self.tracker.login(email, current_password)
                if login_response.get('status') == 'SUCCESS':
                    response = self.tracker.change_password(
                        email,
                        login_response.get('session', ''),
                        new_password
                    )
                else:
                    self.set_status("❌ Credenciales inválidas", True)
                    return

            if response.get('status') == 'SUCCESS':
                self.set_status("✅ Contraseña cambiada exitosamente")
                dialog.destroy()
            else:
                self.set_status(f"❌ {response.get('message', 'Error al cambiar la contraseña')}", True)

        btn_frame = ttk.Frame(dialog, padding="10")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Button(
            btn_frame,
            text="Cambiar Contraseña",
            style="primary.TButton",
            command=handle_change
        ).pack(fill=tk.X)

    def create_habit_section(self):
        # Frame superior
        top_frame = ttk.Frame(self.habits_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Campos para nuevo hábito
        ttk.Label(top_frame, text="Nombre:").pack(side=tk.LEFT, padx=(0, 5))
        self.habit_name_entry = ttk.Entry(top_frame, width=20)
        self.habit_name_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="Descripción:").pack(side=tk.LEFT, padx=(10, 5))
        self.habit_desc_entry = ttk.Entry(top_frame, width=30)
        self.habit_desc_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="Frecuencia:").pack(side=tk.LEFT, padx=(10, 5))
        self.frequency_var = tk.StringVar(value="diaria")
        self.frequency_combo = ttk.Combobox(
            top_frame,
            textvariable=self.frequency_var,
            values=FREQUENCY_OPTIONS,
            width=10,
            state="readonly"
        )
        self.frequency_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            top_frame,
            text="Añadir",
            style="primary.TButton",
            command=self.add_habit
        ).pack(side=tk.LEFT, padx=5)

        # Lista de hábitos
        columns = ("id", "nombre", "descripcion", "frequency", "estado")
        self.habits_tree = ttk.Treeview(
            self.habits_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configurar columnas
        self.habits_tree.heading("id", text="ID")
        self.habits_tree.heading("nombre", text="Nombre")
        self.habits_tree.heading("descripcion", text="Descripción")
        self.habits_tree.heading("frequency", text="Frecuencia")
        self.habits_tree.heading("estado", text="Estado")

        # Ajustar anchos
        self.habits_tree.column("id", width=50)
        self.habits_tree.column("nombre", width=150)
        self.habits_tree.column("descripcion", width=200)
        self.habits_tree.column("frequency", width=100)
        self.habits_tree.column("estado", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.habits_frame, orient=tk.VERTICAL, command=self.habits_tree.yview)
        self.habits_tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar elementos
        self.habits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Botones de acción
        btn_frame = ttk.Frame(self.habits_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame,
            text="Actualizar Lista",
            style="info.TButton",
            command=self.refresh_habits
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Completar",
            style="success.TButton",
            command=self.show_complete_habit_dialog
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Eliminar",
            style="danger.TButton",
            command=self.delete_habit
        ).pack(side=tk.LEFT, padx=5)

    def set_status(self, message, is_error=False):
        """Actualiza el mensaje de estado."""
        self.status_var.set(message)
        if is_error:
            self.status_label.configure(style='Danger.TLabel')
        else:
            self.status_label.configure(style='Success.TLabel')

    def register_user(self):
        """Maneja el registro de usuario."""
        email = self.email_entry.get().strip()
        if not email:
            self.set_status("❌ El email es requerido", True)
            return

        response = self.tracker.register(email)
        if response.get('status') == 'SUCCESS':
            self.set_status("✅ Registro exitoso. Revisa tu correo para completar el proceso.")
            self.email_entry.delete(0, tk.END)
        else:
            self.set_status(f"❌ {response.get('message', 'Error en el registro')}", True)

    def login_user(self):
        """Maneja el inicio de sesión."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            self.set_status("❌ Email y contraseña son requeridos", True)
            return

        response = self.tracker.login(email, password)

        if response.get('status') == 'NEW_PASSWORD_REQUIRED':
            self.show_change_password_dialog()
        elif response.get('status') == 'SUCCESS':
            self.set_status("✅ Inicio de sesión exitoso")
            self.notebook.tab(1, state="normal")
            self.notebook.select(1)
            self.refresh_habits()
        else:
            self.set_status(f"❌ {response.get('message', 'Error en el inicio de sesión')}", True)

    def refresh_habits(self):
        """Actualiza la lista de hábitos."""
        for item in self.habits_tree.get_children():
            self.habits_tree.delete(item)

        habits = self.tracker.get_habits()
        if habits:
            for habit in habits:
                # Convertir la frecuencia de inglés a español
                frequency_es = FREQUENCY_MAP.get(habit.get('frequency', 'daily'), 'diaria')

                # Asegurarse de obtener la descripción correctamente
                description = habit.get('description')
                if description is None or description.strip() == '':
                    description = 'Sin descripción'

                self.habits_tree.insert('', tk.END, values=(
                    habit['id'],
                    habit['name'],
                    description,
                    frequency_es,
                    'Completado' if habit.get('completed') else 'Pendiente'
                ))

    def add_habit(self):
        """Añade un nuevo hábito."""
        name = self.habit_name_entry.get().strip()
        description = self.habit_desc_entry.get().strip()
        frequency_es = self.frequency_var.get()
        frequency = FREQUENCY_MAP_REVERSE.get(frequency_es, 'daily')  # Convertir a inglés

        if not name:
            self.set_status("❌ El nombre del hábito es requerido", True)
            return

        response = self.tracker.add_habit(name, description, frequency)
        if response.get('status') != 'ERROR':
            self.set_status("✅ Hábito añadido exitosamente")
            self.habit_name_entry.delete(0, tk.END)
            self.habit_desc_entry.delete(0, tk.END)
            self.frequency_var.set("diaria")
            self.refresh_habits()
        else:
            self.set_status(f"❌ {response.get('message', 'Error al añadir el hábito')}", True)

    def show_complete_habit_dialog(self):
        """Muestra diálogo para completar hábito."""
        selected_item = self.habits_tree.selection()
        if not selected_item:
            self.set_status("❌ Por favor, selecciona un hábito", True)
            return

        habit_id = self.habits_tree.item(selected_item)['values'][0]
        habit_name = self.habits_tree.item(selected_item)['values'][1]
        habit_description = self.habits_tree.item(selected_item)['values'][2]
        current_freq_es = self.habits_tree.item(selected_item)['values'][3]
        current_freq = FREQUENCY_MAP_REVERSE.get(current_freq_es, 'daily')

        dialog = tk.Toplevel(self.root)
        dialog.title("Completar Hábito")
        dialog.geometry("400x300")
        dialog.grab_set()

        ttk.Label(
            dialog,
            text=f"Hábito: {habit_name}",
            style="Heading.TLabel"
        ).pack(pady=10)

        if habit_description:
            ttk.Label(
                dialog,
                text=f"Descripción: {habit_description}",
                style="TLabel"
            ).pack(pady=5)

        # Frame para opciones
        options_frame = ttk.Frame(dialog, padding="20")
        options_frame.pack(fill=tk.X)

        # Variable para completado
        completed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Marcar como completado",
            variable=completed_var
        ).pack(fill=tk.X, pady=5)

        # Variable para frecuencia
        freq_var = tk.StringVar(value=current_freq_es)  # Mantener el valor en español en la UI

        ttk.Label(options_frame, text="Frecuencia:").pack(fill=tk.X, pady=(10, 0))
        freq_combo = ttk.Combobox(
            options_frame,
            textvariable=freq_var,
            values=FREQUENCY_OPTIONS,
            state="readonly"
        )
        freq_combo.pack(fill=tk.X, pady=5)

        def handle_update():
            # Convertir la frecuencia seleccionada a inglés antes de enviar
            selected_freq = FREQUENCY_MAP_REVERSE.get(freq_var.get(), 'daily')

            data = {
                "habit_id": habit_id,
                "habit_name": habit_name,
                "completed": completed_var.get(),
                "frequency": selected_freq  # Enviamos la frecuencia en inglés
            }

            # Mostrar resumen
            summary = f"""
           ¿Confirmar los siguientes cambios?

           - Completado: {'Sí' if completed_var.get() else 'No'}
           - Frecuencia: {freq_var.get()}
           """
            if messagebox.askyesno("Confirmar cambios", summary):
                logger_msg = f"Enviando actualización: {data}"
                print(logger_msg)  # Para debugging

                response = self.tracker.update_habit(habit_id, data)
                if response.get('status') != 'ERROR':
                    self.set_status("✅ Hábito actualizado exitosamente")
                    self.refresh_habits()
                    dialog.destroy()
                else:
                    error_msg = response.get('message', 'Error al actualizar el hábito')
                    print(f"Error en actualización: {error_msg}")  # Para debugging
                    self.set_status(f"❌ {error_msg}", True)

        ttk.Button(
            dialog,
            text="Actualizar Hábito",
            style="primary.TButton",
            command=handle_update
        ).pack(pady=20)
    def complete_habit(self):
        """Marca un hábito como completado."""
        selected_item = self.habits_tree.selection()
        if not selected_item:
            self.set_status("❌ Por favor, selecciona un hábito", True)
            return

        habit_id = self.habits_tree.item(selected_item)['values'][0]
        habit_name = self.habits_tree.item(selected_item)['values'][1]
        self.show_complete_habit_dialog(habit_id, habit_name)

    def delete_habit(self):
        """Elimina un hábito."""
        selected_item = self.habits_tree.selection()
        if not selected_item:
            self.set_status("❌ Por favor, selecciona un hábito", True)
            return

        habit_id = self.habits_tree.item(selected_item)['values'][0]
        habit_name = self.habits_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Estás seguro de eliminar el hábito '{habit_name}'?"):
            response = self.tracker.delete_habit(habit_id)
            if response.get('status') != 'ERROR':
                self.set_status("✅ Hábito eliminado exitosamente")
                self.refresh_habits()
            else:
                self.set_status(f"❌ {response.get('message', 'Error al eliminar el hábito')}", True)
def main():
    try:
        print("Iniciando Habit Tracker...")
        root = tk.Tk()
        tracker_ui = ModernHabitTrackerUI(root)
        print("Aplicación iniciada exitosamente.")
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)