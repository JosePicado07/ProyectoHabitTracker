from habit_tracker import HabitTracker

def main():
    tracker = HabitTracker()

    while True:
        print("\nOpciones:")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Añadir hábito")
        print("4. Completar hábito")
        print("5. Eliminar hábito")
        print("6. Listar hábitos")
        print("7. Salir")

        choice = input("Selecciona una opción: ")

        if choice == '1':
            email = input("Introduce tu correo electrónico: ")
            password = input("Introduce tu contraseña: ")
            user_id = tracker.register_user(email, password)
            if 'Error' not in str(user_id):
                print(f"Usuario registrado con ID: {user_id}")
                print("Por favor, verifica tu correo electrónico antes de iniciar sesión")
            else:
                print(user_id)

        elif choice == '2':
            email = input("Introduce tu correo electrónico: ")
            password = input("Introduce tu contraseña: ")
            token = tracker.login_user(email, password)
            if 'Error' not in str(token):
                print("Inicio de sesión exitoso")
            else:
                print(token)

        elif choice == '3':
            if not tracker.token:
                print("Debes iniciar sesión primero")
                continue
            habit_name = input("Introduce el nombre del hábito: ")
            frequency = input("Introduce la frecuencia (diaria/semanal/mensual): ")
            if not frequency:
                frequency = "diaria"
            print(tracker.add_habit(habit_name, frequency))

        elif choice == '4':
            if not tracker.token:
                print("Debes iniciar sesión primero")
                continue
            habit_name = input("Introduce el nombre del hábito que deseas marcar como completado: ")
            print(tracker.complete_habit(habit_name))

        elif choice == '5':
            if not tracker.token:
                print("Debes iniciar sesión primero")
                continue
            habit_name = input("Introduce el nombre del hábito que deseas eliminar: ")
            print(tracker.delete_habit(habit_name))

        elif choice == '6':
            if not tracker.token:
                print("Debes iniciar sesión primero")
                continue
            habits = tracker.list_habits()
            print(habits)

        elif choice == '7':
            print("Saliendo...")
            break

        else:
            print("Opción no válida, por favor intenta de nuevo.")

if __name__ == "__main__":
    main()