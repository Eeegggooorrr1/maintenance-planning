-- 1. Список устройств
SELECT id, name, category, brand, model FROM devices ORDER BY name;

-- 2. Список задач
SELECT id, title, scheduled_date, status FROM tasks ORDER BY scheduled_date;

-- 3. Устройства заданной категории (параметр: категория)
SELECT id, name, category FROM devices WHERE category = ? ORDER BY name;

-- 4. Активные задачи до даты (параметр: дата YYYY-MM-DD)
SELECT id, title, scheduled_date FROM tasks
WHERE status IN ('planned', 'in_progress') AND scheduled_date <= ?
ORDER BY scheduled_date;

-- 5. Задачи и устройства
SELECT t.id, t.title, d.name AS device_name FROM tasks AS t
JOIN devices AS d ON d.id = t.device_id ORDER BY t.id;

-- 6. Задачи, устройства и владельцы
SELECT t.title, d.name AS device_name, u.name AS owner_name FROM tasks AS t
JOIN devices AS d ON d.id = t.device_id
JOIN users AS u ON u.id = t.owner_id ORDER BY t.id;

-- 7. Количество устройств
SELECT COUNT(*) AS device_count FROM devices;

-- 8. Количество активных задач
SELECT COUNT(*) AS active_count FROM tasks WHERE status IN ('planned', 'in_progress');

-- 9. Количество задач по статусу
SELECT status, COUNT(*) AS task_count FROM tasks GROUP BY status ORDER BY status;

-- 10. Количество задач по устройству, включая устройства без задач
SELECT d.id, d.name, COUNT(t.id) AS task_count FROM devices AS d
LEFT JOIN tasks AS t ON t.device_id = d.id
GROUP BY d.id, d.name ORDER BY d.name;

-- 11. Устройства с минимум одной задачей
SELECT d.id, d.name, COUNT(t.id) AS task_count FROM devices AS d
LEFT JOIN tasks AS t ON t.device_id = d.id
GROUP BY d.id, d.name HAVING COUNT(t.id) >= 1 ORDER BY d.name;
