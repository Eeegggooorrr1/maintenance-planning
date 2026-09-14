from datetime import date, timedelta


def schedule_next_service(
        last_service_date: date,
        interval_days: int
) -> date:
    if interval_days <= 0:
        raise ValueError("Интервал обслуживания должен быть положительным")
    return last_service_date + timedelta(days=interval_days)


def get_over_tasks(
        tasks: list[dict],
        current_date: date
) -> list[dict]:
    return [
        item for item in tasks
        if not item["done"] and item["service_date"] < current_date
    ]


def get_service_status(
        device_name: str,
        service_date: date,
        current_date: date
) -> str:
    days_until_service = (service_date - current_date).days

    if days_until_service < 0:
        return (
            f"Обслуживание устройства «{device_name}» просрочено "
            f"на {abs(days_until_service)} дн"
        )

    if days_until_service == 0:
        return (
            f"Сегодня необходимо выполнить обслуживание устройства "
            f"«{device_name}»"
        )

    return (
        f"Обслуживание устройства «{device_name}» запланировано "
        f"через {days_until_service} дн."
    )


device = "Стиральная машина"
serv_date = date(2026, 9, 20)
curr_date = date(2026, 9, 13)

print("Система планирования обслуживания бытовой техники")
print(f"Устройство: {device}")
print(f"Дата обслуживания: {serv_date}")
print(get_service_status(
    device,
    serv_date,
    curr_date
))

device = "Стиральная машина 2"
serv_date = date(2026, 9, 20)
curr_date = date(2026, 9, 23)

print("Система планирования обслуживания бытовой техники")
print(f"Устройство: {device}")
print(f"Дата обслуживания: {serv_date}")
print(get_service_status(
    device,
    serv_date,
    curr_date
))

last_service = date(2026, 6, 10)
next_service = schedule_next_service(last_service, 180)
print(get_service_status(device, next_service, curr_date))

curr_tasks = [
    {
        "device_name": "Стиральная машина",
        "service_date": date(2026, 9, 20),
        "done": False,
    },
    {
        "device_name": "Холодильник",
        "service_date": date(2026, 9, 1),
        "done": False,
    },
    {
        "device_name": "Пылесос",
        "service_date": date(2026, 8, 25),
        "done": True,
    },
    {
        "device_name": "Микроволновка",
        "service_date": date(2026, 9, 10),
        "done": False,
    },
]

over = get_over_tasks(curr_tasks, curr_date)
print(f"Просроченных задач: {len(over)}")
for task in over:
    print(f"  - {task['device_name']} (срок: {task['service_date']})")