.PHONY: install test lint dev

install:
	python -m pip install -r backend/requirements-dev.txt
	cd frontend && npm install

test:
	cd backend && pytest -q
	cd frontend && npm test

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

dev:
	docker compose up --build

