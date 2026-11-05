.PHONY: format lint check test run run-web django-check static-check db-import sql-check web-check

format:
	poetry run isort src tests homepage devices maintenance_tasks maintenance_web manage.py
	poetry run black src tests homepage devices maintenance_tasks maintenance_web manage.py

lint:
	poetry run flake8 src tests homepage devices maintenance_tasks maintenance_web manage.py

check:
	poetry run pre-commit run --all-files

test:
	poetry run pytest -v

run:
	poetry run python -m maintenance_planning.main

run-web:
	poetry run python manage.py runserver

django-check:
	poetry run python manage.py check

static-check:
	poetry run python manage.py findstatic homepage/css/style.css
	poetry run python manage.py findstatic homepage/js/main.js
	poetry run python manage.py findstatic homepage/img/logo.svg

db-import:
	poetry run python -m db.import_json

sql-check:
	poetry run python -c "import sqlite3; c=sqlite3.connect('data/maintenance.sqlite'); c.executescript(open('sql/schema.sql', encoding='utf-8').read()); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall()); c.close()"

web-check: django-check static-check test lint

.PHONY: migrate orm-import migrations-check
migrate:
	poetry run python manage.py migrate

orm-import:
	poetry run python manage.py import_pr7

migrations-check:
	poetry run python manage.py makemigrations --check --dry-run
	poetry run python manage.py showmigrations
