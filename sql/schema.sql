PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    serial_number TEXT NOT NULL DEFAULT '',
    last_service_date TEXT,
    service_interval_days INTEGER NOT NULL CHECK (service_interval_days > 0),
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    device_id INTEGER NOT NULL REFERENCES devices(id),
    title TEXT NOT NULL,
    scheduled_date TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 3),
    status TEXT NOT NULL CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_tasks_device ON tasks(device_id);
