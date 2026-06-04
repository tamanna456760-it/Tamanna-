.PHONY: help install dev test lint format clean build run

help:
	@echo "Tamanna AI - Available Commands"
	@echo "================================"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run in development mode"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build files"
	@echo "  make build      - Build project"
	@echo "  make run        - Run application"

install:
	pip install -r requirements.txt

npm_install:
	npm install

dev:
	python -m uvicorn src.core.main:app --reload

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ --max-line-length=120
	pylint src/
	eslint . --ext .js,.jsx,.ts,.tsx 2>/dev/null || true

format:
	black src/
	isort src/
	prettier --write "**/*.{js,jsx,ts,tsx,json,md,css}"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ .eggs/ *.egg-info/
	rm -rf .coverage .pytest_cache/ .mypy_cache/

type-check:
	mypy src/

build:
	python setup.py build

run:
	python main.py

all: clean install lint format test
