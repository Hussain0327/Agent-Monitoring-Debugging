.PHONY: dev dev-server dev-dashboard test test-sdk test-server test-dashboard lint lint-py lint-ts \
       docker-up docker-down migrate format install

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: dev-server dev-dashboard

dev-server:
	cd server && uvicorn vigil_server.main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard:
	cd dashboard && npm run dev

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

install:
	cd sdk && pip install -e ".[dev]"
	cd server && pip install -e ".[dev]"
	cd dashboard && npm install

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: test-sdk test-server test-dashboard

test-sdk:
	cd sdk && python -m pytest tests/ -v

test-server:
	cd server && python -m pytest tests/ -v

test-dashboard:
	cd dashboard && npm test

# ---------------------------------------------------------------------------
# Linting & Formatting
# ---------------------------------------------------------------------------

lint: lint-py lint-ts

lint-py:
	ruff check sdk/src server/src
	ruff format --check sdk/src server/src
	mypy sdk/src server/src

lint-ts:
	cd dashboard && npm run lint

format:
	ruff format sdk/src server/src
	ruff check --fix sdk/src server/src

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate:
	cd server && alembic upgrade head

migrate-new:
	cd server && alembic revision --autogenerate -m "$(msg)"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v
