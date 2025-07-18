.PHONY: help install test lint format type-check clean docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies with Poetry"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run linting (flake8)"
	@echo "  format      - Format code (black + isort)"
	@echo "  type-check  - Run type checking (mypy)"
	@echo "  clean       - Clean cache and build artifacts"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-up   - Start services with docker-compose"
	@echo "  docker-down - Stop services"
	@echo "  docker-logs - View logs"
	@echo "  api-server  - Start API server locally"
	@echo "  todo-cli    - Run todo CLI"
	@echo "  file-org    - Run file organizer CLI"

# Development setup
install:
	poetry install

# Testing
test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=apps --cov=shared --cov-report=html --cov-report=term

# Code quality
lint:
	poetry run flake8 apps shared tests

format:
	poetry run black apps shared tests
	poetry run isort apps shared tests

type-check:
	poetry run mypy apps shared

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

# Docker commands
docker-build:
	docker build -t python-cli .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Application commands
api-server:
	poetry run api-server

todo-cli:
	poetry run todo-cli

file-org:
	poetry run file-organizer

# CLI Tools in Docker
docker-cli:
	docker-compose run --rm cli-tools bash

docker-todo:
	docker-compose run --rm cli-tools poetry run todo-cli

docker-file-org:
	docker-compose run --rm cli-tools poetry run file-organizer

# Development workflow
dev-setup: install
	@echo "Setting up development environment..."
	mkdir -p data logs
	@echo "Development environment ready!"

dev-test: format lint type-check test
	@echo "All development checks passed!"

# Quick start
quick-start: dev-setup
	@echo "Starting API server..."
	poetry run api-server

# Full stack with Docker
stack-up: docker-build docker-up
	@echo "Full stack is running!"
	@echo "API Server: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Flower (Celery): http://localhost:5555"

stack-down: docker-down
	@echo "Stack stopped."

# Show project stats
stats:
	@echo "Project Statistics:"
	@echo "=================="
	@find apps shared -name "*.py" | wc -l | xargs echo "Python files:"
	@find apps shared -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "Lines of code: " $$1}'
	@find tests -name "*.py" | wc -l | xargs echo "Test files:"
	@find tests -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "Lines of tests: " $$1}'

# Check project health
health-check:
	@echo "Checking project health..."
	poetry check
	poetry run python -c "import apps.api_server, apps.todo_cli, apps.file_organizer; print('All imports successful')"
	@echo "Project health check passed!"

# Pre-commit checks
precommit: format lint type-check test
	@echo "Pre-commit checks completed successfully!"