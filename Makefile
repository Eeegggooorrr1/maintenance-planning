.PHONY: format lint check test run run-web django-check static-check web-check

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

web-check: django-check static-check test lint
