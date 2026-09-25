.PHONY: install fmt lint test check

install:
	uv sync --locked

fmt:
	uv run ruff format .

lint:
	uv run ruff check .

test:
	uv run pytest


check:
	uv run ruff format --check .
	uv run ruff check .
	uv run pytest
