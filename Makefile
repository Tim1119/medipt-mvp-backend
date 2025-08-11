.PHONY: install test lint format clean run migrate shell collect-static setup-pre-commit test-coverage

# Installation and setup
install:
	pip install -r requirements.txt
	python manage.py migrate
	python manage.py collectstatic --noinput

# Testing
test:
	python manage.py test

test-coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html

# Code quality
lint:
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

# Development
run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

shell:
	python manage.py shell_plus

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .coverage

# Production
collect-static:
	python manage.py collectstatic --noinput

# Pre-commit setup
setup-pre-commit:
	pre-commit install
