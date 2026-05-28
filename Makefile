	.PHONY: install dev run test smoke docker
install:
	pip install -e .[test]

dev:
	uvicorn devcareerbridge.main:app --reload

run:
	uvicorn devcareerbridge.main:app

test:
	pytest -q

smoke:
	python -m httpx http://localhost:8000/api/health

docker:
	docker build -t devcareerbridge .
