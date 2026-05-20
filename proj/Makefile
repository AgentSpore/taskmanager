# Makefile for TaskManager
.PHONY: install dev run test smoke docker clean build publish

# Default target
all: install

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
dev:
	pip install -e .[dev]

# Run the application in development mode
run: dev
	uvicorn taskmanager.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test: dev
	pytest tests/ -v

# Run smoke test
smoke: dev
	python smoke_test.py

# Build Docker image
docker:
	docker build -t taskmanager:latest .

# Build Docker image for production
build: docker
	docker build -f Dockerfile --target runtime -t taskmanager:runtime .

# Publish to Docker Hub (requires authentication)
publish: build
	docker tag taskmanager:latest taskmanager/taskmanager:latest
	docker push taskmanager/taskmanager:latest

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	docker rmi taskmanager:latest taskmanager:runtime 2>/dev/null || true

# Lint code
lint: dev
	ruff check src/ tests/
	black --check src/ tests/

# Format code
format: dev
	black src/ tests/
	ruff check --fix src/ tests/

# Development environment setup
setup: dev
	pip install pre-commit
	pre-commit install

# Run pre-commit hooks
precommit:
	pre-commit run --all-files

# Build documentation
docs:
	cd docs && make html

# Serve documentation
docs-serve:
	cd docs && make serve

# Run all checks
check: lint test

# Quick development cycle
dev-check: format check

# Production deployment
deploy: build publish

# Development deployment
dev-deploy: test docker
	docker run -p 8000:8000 taskmanager:latest