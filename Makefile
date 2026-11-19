.PHONY: install fmt lint test check db-down db-up

install:
	uv sync --locked

fmt:
	uv run ruff format .

lint:
	uv run ruff check .

test:
	uv run pytest

db-up:
	docker compose up -d --wait

db-down:
	docker compose down

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run pyright
	uv run pytest --cov=parking_reservation --cov-report=term-missing:skip-covered
