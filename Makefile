.PHONY: format lint check test run run-web django-check

format:
	poetry run isort src tests
	poetry run black src tests

lint:
	poetry run flake8 src tests

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
