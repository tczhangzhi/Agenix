.PHONY: help test test-all test-unit test-integration coverage lint format type-check clean install dev-install docs

help:
	@echo "Available targets:"
	@echo "  install         - Install package"
	@echo "  dev-install     - Install package with dev dependencies"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  coverage        - Run tests with coverage report"
	@echo "  lint            - Run linters (black, isort, flake8)"
	@echo "  format          - Format code with black and isort"
	@echo "  type-check      - Run type checker (mypy)"
	@echo "  clean           - Clean build artifacts"
	@echo "  docs            - Build documentation"

install:
	pip install -e .

dev-install:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "not integration"

test-integration:
	pytest tests/integration/ -v -m integration

coverage:
	pytest tests/ -v --cov=agenix --cov-report=html --cov-report=term

lint:
	black --check agenix/ tests/
	isort --check-only agenix/ tests/
	flake8 agenix/ tests/

format:
	black agenix/ tests/
	isort agenix/ tests/

type-check:
	mypy agenix/ --ignore-missing-imports

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .tox/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && make html

.DEFAULT_GOAL := help
