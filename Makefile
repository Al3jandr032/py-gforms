.PHONY: help install install-dev test test-unittest lint format type-check clean pre-commit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	uv sync --no-dev

install-dev: ## Install development dependencies
	uv sync --all-extras

test: ## Run tests with pytest
	uv run pytest tests/ -v --cov=src/gforms --cov-report=term-missing

test-unittest: ## Run tests with unittest
	uv run python -m unittest discover tests/ -p "test_*_unittest.py" -v

test-all: ## Run both pytest and unittest tests
	@echo "Running pytest tests..."
	@make test
	@echo ""
	@echo "Running unittest tests..."
	@make test-unittest

lint: ## Run linting
	uv run flake8 src/ tests/
	uv run mypy src/

format: ## Format code
	uv run black src/ tests/
	uv run isort src/ tests/

type-check: ## Run type checking
	uv run mypy src/

clean: ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

pre-commit: ## Install pre-commit hooks
	uv run pre-commit install

check: lint test ## Run all checks (lint + test)
