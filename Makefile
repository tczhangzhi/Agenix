.PHONY: help install test clean build upload upload-test check docs

help:
	@echo "Agenix - Development Commands"
	@echo ""
	@echo "make install      - Install package in development mode"
	@echo "make dev          - Install with dev dependencies"
	@echo "make docs         - Install with docs dependencies"
	@echo "make test         - Run all tests"
	@echo "make clean        - Clean build artifacts"
	@echo "make build        - Build distribution packages"
	@echo "make check        - Check package before upload"
	@echo "make upload-test  - Upload to TestPyPI"
	@echo "make upload       - Upload to PyPI"

install:
	pip install -e .

dev:
	pip install -e .[dev]

docs:
	pip install -e .[docs]

test:
	pytest tests/ -v

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build: clean
	pip install --upgrade build
	python -m build

check: build
	pip install --upgrade twine
	twine check dist/*

upload-test: check
	twine upload --repository testpypi dist/*
	@echo ""
	@echo "Test installation with:"
	@echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agenix"

upload: check
	twine upload dist/*
	@echo ""
	@echo "Published to PyPI!"
	@echo "Install with: pip install agenix"

.DEFAULT_GOAL := help
