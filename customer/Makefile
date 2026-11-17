.PHONY: lint format-check typecheck test build check

lint:
	uv run --no-sync ruff check .

format-check:
	uv run --no-sync ruff format --check .

typecheck:
	uv run --no-sync pyright

test:
	uv run --no-sync pytest -q

build:
	uv build

check: lint format-check typecheck test build
