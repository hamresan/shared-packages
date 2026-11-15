.PHONY: sync check lint format-check typecheck test build benchmark

sync:
	uv sync --frozen --group dev

check: lint format-check typecheck test build

lint:
	uv run --frozen ruff check .

format-check:
	uv run --frozen ruff format --check .

typecheck:
	uv run --frozen pyright

test:
	uv run --frozen pytest

build:
	uv build

benchmark:
	uv run --frozen python -m benchmarks.availability_benchmark
