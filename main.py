from datetime import date


def get_service_status(
    device_name: str,
    service_date: date,
    current_date: date
) -> str:

    days_until_service = (service_date - current_date).days

    if days_until_service < 0:
        return f"Обслуживание устройства «{device_name}» просрочено на {abs(days_until_service)} дн"

    if days_until_service == 0:
        return f"Сегодня необходимо выполнить обслуживание устройства «{device_name}»"

    return (
        f"Обслуживание устройства «{device_name}» запланировано "
        f"через {days_until_service} дн."
    )


device_name = "Стиральная машина"
service_date = date(2026, 9, 20)
current_date = date(2026, 9, 13)


print("Система планирования обслуживания бытовой техники")
print(f"Устройство: {device_name}")
print(f"Дата обслуживания: {service_date}")
print(get_service_status(
    device_name,
    service_date,
    current_date
))

device_name = "Стиральная машина 2"
service_date = date(2026, 9, 20)
current_date = date(2026, 9, 23)

print("Система планирования обслуживания бытовой техники")
print(f"Устройство: {device_name}")
print(f"Дата обслуживания: {service_date}")
print(get_service_status(
    device_name,
    service_date,
    current_date
))