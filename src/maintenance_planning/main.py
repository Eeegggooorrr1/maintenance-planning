from datetime import date

from .config import Settings
from .model import User
from .repo import DeviceRepository, TaskRepository, UserRepository
from .service import AuthService, DeviceService, TaskService


def _input_date(prompt: str) -> date:
    return date.fromisoformat(input(prompt).strip())


def _print_devices(service: DeviceService, user: User) -> None:
    devices = service.list_for_user(user.id)
    print("\nУстройства:")
    if not devices:
        print("  Пока нет устройств")
    for device in devices:
        print(
            f"  {device} | следующее обслуживание:"
            f" {device.next_service_date or 'не задано'}"
        )


def _print_tasks(service: TaskService, user: User) -> None:
    tasks = service.list_for_user(user.id)
    print("\nЗадачи:")
    if not tasks:
        print("  Пока нет задач")
    for task in tasks:
        print(f"  {task}")


def main() -> None:
    settings = Settings.from_env()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    users = UserRepository(settings.data_dir / "users.json")
    device_repository = DeviceRepository(settings.data_dir / "devices.json")
    task_repository = TaskRepository(settings.data_dir / "tasks.json")
    device_service = DeviceService(
        device_repository, settings.default_service_interval_days
    )
    task_service = TaskService(task_repository, device_repository)
    auth = AuthService(users)
    print(settings.app_name)
    print("Демонстрационный вход: JWT пока заменен выбором пользователя.")
    name = input("Ваше имя: ").strip() or "Гость"
    email = input("Email: ").strip() or "guest@example.com"
    user = auth.login_or_create(name, email)
    print(f"Добро пожаловать, {user.name}!")
    while True:
        print("\n1 - устройства  2 - задачи  3 - добавить устройство")
        print("4 - добавить задачу  5 - завершить задачу  0 - выход")
        choice = input("> ").strip()
        try:
            if choice == "1":
                _print_devices(device_service, user)
            elif choice == "2":
                _print_tasks(task_service, user)
            elif choice == "3":
                device = device_service.create(
                    user.id,
                    input("Название: "),
                    input("Категория: "),
                    brand=input("Бренд: "),
                    model=input("Модель: "),
                )
                print(f"Добавлено: {device}")
            elif choice == "4":
                _print_devices(device_service, user)
                task = task_service.create(
                    user.id,
                    int(input("ID устройства: ")),
                    input("Название задачи: "),
                    _input_date("Дата (ГГГГ-ММ-ДД): "),
                )
                print(f"Добавлено: {task}")
            elif choice == "5":
                _print_tasks(task_service, user)
                task_id = int(input('ID задачи: '))
                completed = task_service.complete(task_id, user.id)
                print(f"Завершено: {completed}")
            elif choice == "0":
                break
            else:
                print("Неизвестная команда")
        except (ValueError, KeyError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
