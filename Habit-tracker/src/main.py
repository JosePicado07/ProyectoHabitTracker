# main.py
from habit_tracker import HabitTracker

def print_response(response):
    """
    Imprime la respuesta de manera formateada.
    """
    if isinstance(response, dict):
        if 'error' in response:
            print(f"\nError: {response['error']}")
        elif 'message' in response:
            print(f"\nMensaje: {response['message']}")
        else:
            print("\nRespuesta:", response)
    else:
        print("\nRespuesta:", response)


def main():
    tracker = HabitTracker()

    while True:
        print("\n=== Habit Tracker ===")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Cambiar contraseña")
        print("4. Añadir hábito")
        print("5. Listar hábitos")
        print("6. Completar hábito")
        print("7. Eliminar hábito")
        print("8. Ver historial de hábito")
        print("9. Cerrar sesión")
        print("0. Salir")

        choice = input("\nSelecciona una opción: ")

        if choice == '1':
            email = input("Email: ")
            password = input("Contraseña: ")
            response = tracker.register(email, password)
            print_response(response)

            # Si se requiere cambio de contraseña
            if response.get('status') == 'NEW_PASSWORD_REQUIRED':
                print("\nSe requiere cambiar la contraseña.")
                new_password = input("Nueva contraseña: ")
                change_response = tracker.change_password(
                    email,
                    response.get('session'),
                    new_password
                )
                print_response(change_response)

        elif choice == '2':
            email = input("Email: ")
            password = input("Contraseña: ")
            response = tracker.login(email, password)
            print_response(response)

        elif choice == '3':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            current_password = input("Contraseña actual: ")
            new_password = input("Nueva contraseña: ")
            response = tracker.change_password(email, current_password, new_password)
            print_response(response)

        elif choice == '4':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            name = input("Nombre del hábito: ")
            description = input("Descripción (opcional): ")
            frequency = input("Frecuencia (daily/weekly/monthly) [daily]: ") or "daily"
            response = tracker.add_habit(name, description, frequency)
            print_response(response)

        elif choice == '5':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            response = tracker.get_habits()
            print("\nTus hábitos:")
            if isinstance(response, list):
                for habit in response:
                    print(f"- {habit['name']}: {habit.get('description', 'Sin descripción')}")
            else:
                print_response(response)

        elif choice == '6':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            habits = tracker.get_habits()
            if isinstance(habits, list) and habits:
                print("\nSelecciona un hábito para completar:")
                for i, habit in enumerate(habits, 1):
                    print(f"{i}. {habit['name']}")
                try:
                    index = int(input("Número del hábito: ")) - 1
                    if 0 <= index < len(habits):
                        response = tracker.complete_habit(habits[index]['id'])
                        print_response(response)
                    else:
                        print("\nNúmero de hábito inválido")
                except ValueError:
                    print("\nPor favor, ingresa un número válido")
            else:
                print("\nNo hay hábitos disponibles")

        elif choice == '7':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            habits = tracker.get_habits()
            if isinstance(habits, list) and habits:
                print("\nSelecciona un hábito para eliminar:")
                for i, habit in enumerate(habits, 1):
                    print(f"{i}. {habit['name']}")
                try:
                    index = int(input("Número del hábito: ")) - 1
                    if 0 <= index < len(habits):
                        confirm = input(f"¿Estás seguro de eliminar '{habits[index]['name']}'? (s/n): ")
                        if confirm.lower() == 's':
                            response = tracker.delete_habit(habits[index]['id'])
                            print_response(response)
                    else:
                        print("\nNúmero de hábito inválido")
                except ValueError:
                    print("\nPor favor, ingresa un número válido")
            else:
                print("\nNo hay hábitos disponibles")

        elif choice == '8':
            if not tracker.is_authenticated:
                print("\nDebes iniciar sesión primero")
                continue
            habits = tracker.get_habits()
            if isinstance(habits, list) and habits:
                print("\nSelecciona un hábito para ver su historial:")
                for i, habit in enumerate(habits, 1):
                    print(f"{i}. {habit['name']}")
                try:
                    index = int(input("Número del hábito: ")) - 1
                    if 0 <= index < len(habits):
                        response = tracker.get_habit_history(habits[index]['id'])
                        if isinstance(response, list):
                            print(f"\nHistorial de '{habits[index]['name']}':")
                            for entry in response:
                                print(f"- Completado: {entry['completed_at']}")
                        else:
                            print_response(response)
                    else:
                        print("\nNúmero de hábito inválido")
                except ValueError:
                    print("\nPor favor, ingresa un número válido")
            else:
                print("\nNo hay hábitos disponibles")

        elif choice == '9':
            response = tracker.logout()
            print_response(response)

        elif choice == '0':
            print("\n¡Hasta luego!")
            break

        else:
            print("\nOpción no válida")


if __name__ == "__main__":
    main()