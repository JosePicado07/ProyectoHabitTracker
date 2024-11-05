# main.py
from habit_tracker import HabitTracker


def print_response(response):
    """Imprime la respuesta de manera formateada."""
    if isinstance(response, dict):
        if 'error' in response:
            print(f"\nError: {response['error']}")
        elif 'message' in response:
            print(f"\nMensaje: {response['message']}")
        else:
            print("\nRespuesta:", response)
    else:
        print("\nRespuesta:", response)


def print_password_requirements():
    """Imprime los requisitos de la contraseña."""
    print("\nLa contraseña debe contener:")
    print("- Al menos 8 caracteres")
    print("- Al menos una letra mayúscula")
    print("- Al menos una letra minúscula")
    print("- Al menos un número")
    print("- Al menos un carácter especial")


def get_new_password() -> str:
    """Solicita y valida la nueva contraseña."""
    while True:
        new_password = input("\nNueva contraseña: ")
        confirm_password = input("Confirmar nueva contraseña: ")

        if new_password != confirm_password:
            print("\n❌ Las contraseñas no coinciden. Intente nuevamente.")
            continue

        return new_password


def main():
    tracker = HabitTracker()
    current_email = None

    while True:
        print("\n=== Habit Tracker ===")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Cambiar contraseña")
        print("4. Añadir hábito")
        print("5. Listar hábitos")
        print("6. Completar hábito")
        print("7. Eliminar hábito")
        print("9. Cerrar sesión")
        print("0. Salir")

        choice = input("\nSelecciona una opción: ").strip()

        if choice == '1':
            email = input("Email: ").strip()
            response = tracker.register(email)
            print_response(response)

        elif choice == '2':
            email = input("Email: ").strip()
            current_email = email
            password = input("Contraseña: ")
            response = tracker.login(email, password)
            print_response(response)

            if response.get('status') == 'NEW_PASSWORD_REQUIRED':
                print("\n⚠️  Se requiere cambiar la contraseña temporal.")
                print_password_requirements()

                while True:
                    new_password = get_new_password()
                    change_response = tracker.change_password(
                        email,
                        response.get('session'),
                        new_password
                    )

                    if change_response.get('status') == 'ERROR' and 'seguridad' in change_response.get('message',
                                                                                                       '').lower():
                        print("\n❌ La contraseña no cumple con los requisitos de seguridad. Intente nuevamente.")
                        continue

                    print_response(change_response)
                    break

        elif choice == '3':
            if tracker.needs_password_change():
                print("\n⚠️  Debe cambiar su contraseña temporal.")
                print_password_requirements()

                while True:
                    new_password = get_new_password()
                    response = tracker.change_password(None, None, new_password)

                    if response.get('status') == 'ERROR' and 'seguridad' in response.get('message', '').lower():
                        print("\n❌ La contraseña no cumple con los requisitos de seguridad. Intente nuevamente.")
                        continue

                    print_response(response)
                    break

            elif not tracker.is_authenticated:
                print("\n❌ Debes iniciar sesión primero")
                continue
            else:
                print_password_requirements()
                current_password = input("\nContraseña actual: ")
                new_password = get_new_password()
                response = tracker.change_password(current_email, current_password, new_password)
                print_response(response)

        elif choice == '4':
            if not tracker.is_authenticated:
                print("\n❌ Debes iniciar sesión primero")
                continue

            name = input("Nombre del hábito: ").strip()
            if not name:
                print("\n❌ El nombre del hábito es requerido")
                continue

            description = input("Descripción (opcional): ").strip()

            while True:
                frequency = input("Frecuencia (daily/weekly/monthly) [daily]: ").strip().lower() or "daily"
                if frequency in ['daily', 'weekly', 'monthly']:
                    break
                print("\n❌ Frecuencia inválida. Use 'daily', 'weekly' o 'monthly'")

            response = tracker.add_habit(name, description, frequency)
            print_response(response)

        # ... (el resto del código permanece igual)


if __name__ == "__main__":
    main()