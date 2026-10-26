from .database import get_connection


def list_devices():
    with get_connection() as connection:
        return connection.execute(
            "SELECT *, date(last_service_date, '+' || service_interval_days "
            "|| ' days') "
            "AS next_service_date FROM devices ORDER BY name"
        ).fetchall()


def find_device(device_id: int):
    with get_connection() as connection:
        return connection.execute(
            "SELECT *, date(last_service_date, '+' || service_interval_days "
            "|| ' days') "
            "AS next_service_date FROM devices WHERE id = ?",
            (device_id,),
        ).fetchone()


def list_tasks():
    with get_connection() as connection:
        return connection.execute(
            "SELECT t.*, d.name AS device_name, u.name AS owner_name "
            "FROM tasks AS t JOIN devices AS d ON d.id = t.device_id "
            "JOIN users AS u ON u.id = t.owner_id ORDER BY t.scheduled_date",
        ).fetchall()


def find_task(task_id: int):
    with get_connection() as connection:
        return connection.execute(
            "SELECT t.*, d.name AS device_name, u.name AS owner_name "
            "FROM tasks AS t JOIN devices AS d ON d.id = t.device_id "
            "JOIN users AS u ON u.id = t.owner_id WHERE t.id = ?",
            (task_id,),
        ).fetchone()


def due_tasks(until: str):
    with get_connection() as connection:
        return connection.execute(
            "SELECT t.*, d.name AS device_name FROM tasks AS t "
            "JOIN devices AS d ON d.id = t.device_id "
            "WHERE t.status IN ('planned', 'in_progress') "
            "AND t.scheduled_date <= ? ORDER BY t.scheduled_date",
            (until,),
        ).fetchall()


def statistics():
    with get_connection() as connection:
        by_device = connection.execute(
            "SELECT d.name, COUNT(t.id) AS task_count FROM devices AS d "
            "LEFT JOIN tasks AS t ON t.device_id = d.id "
            "GROUP BY d.id, d.name ORDER BY d.name"
        ).fetchall()
        by_status = connection.execute(
            "SELECT status, COUNT(*) AS task_count FROM tasks "
            "GROUP BY status ORDER BY status"
        ).fetchall()
    return by_device, by_status
