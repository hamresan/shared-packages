.PHONY: install-dev check lint format-check typecheck test coverage build

install-dev:
	uv sync --extra test --locked

check: lint format-check typecheck coverage build

lint:
	uv run --no-sync ruff check .

format-check:
	uv run --no-sync ruff format --check .

typecheck:
	uv run --no-sync pyright

test:
	uv run --no-sync pytest --no-cov

coverage:
	uv run --no-sync pytest

build:
	uv build
