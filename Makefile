# Makefile for ZestAPI project

.PHONY: help install install-dev test lint format clean build release docs deploy

# Default target
help:
	@echo "ZestAPI Development Commands"
	@echo "=========================="
	@echo "install         Install package dependencies"
	@echo "install-dev     Install development dependencies"
	@echo "test           Run test suite"
	@echo "test-cov       Run tests with coverage"
	@echo "lint           Run linting checks"
	@echo "format         Format code with black and isort"
	@echo "clean          Clean build artifacts"
	@echo "build          Build package"
	@echo "docs           Build documentation"
	@echo "release        Prepare release (requires VERSION)"
	@echo "deploy         Deploy to GitHub and PyPI"
	@echo "deploy-github  Deploy to GitHub only"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	python scripts/dev_setup.py

# Testing
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=zestapi --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 zestapi tests
	mypy zestapi
	black --check zestapi tests
	isort --check-only zestapi tests

format:
	black zestapi tests scripts
	isort zestapi tests scripts

# Build and release
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean test
	python scripts/build.py

release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Please specify VERSION: make release VERSION=1.1.0"; \
		exit 1; \
	fi
	python scripts/release.py $(VERSION)

# Documentation
docs:
	@echo "Building documentation..."
	@echo "Documentation is in docs/ directory"

# Development server
dev:
	python main.py

# Docker
docker-build:
	docker build -t zestapi:latest .

docker-run:
	docker run -p 8000:8000 zestapi:latest

# Deployment
deploy:
	python scripts/deploy.py

deploy-github:
	@echo "Deploying to GitHub..."
	git add .
	git commit -m "Update: $(shell date '+%Y-%m-%d %H:%M')" || true
	git push origin main

# Pre-commit hooks
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
