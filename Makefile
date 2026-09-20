.PHONY: format lint check

format:
	poetry run isort src tests
	poetry run black src tests

lint:
	poetry run flake8 src tests

check:
	poetry run pre-commit run --all-files
