# main.py

from habit_tracker import HabitTracker

def main():
    tracker = HabitTracker()

    while True:
        print("\nOpciones:")
        print("1. Añadir hábito")
        print("2. Completar hábito")
        print("3. Eliminar hábito")
        print("4. Listar hábitos")
        print("5. Salir")

        choice = input("Selecciona una opción: ")

        if choice == '1':
            habit_name = input("Introduce el nombre del hábito: ")
            print(tracker.add_habit(habit_name))
        elif choice == '2':
            habit_name = input("Introduce el nombre del hábito que deseas marcar como completado: ")
            print(tracker.complete_habit(habit_name))
        elif choice == '3':
            habit_name = input("Introduce el nombre del hábito que deseas eliminar: ")
            print(tracker.delete_habit(habit_name))
        elif choice == '4':
            print(tracker.list_habits())
        elif choice == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

if __name__ == "__main__":
    main()
