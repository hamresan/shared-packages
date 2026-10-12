.PHONY: sync lock format lint typecheck test coverage build wheel-smoke check

sync:
	uv sync --extra dev

lock:
	uv lock

format:
	uv run --extra dev ruff format src tests

lint:
	uv run --extra dev ruff check src tests
	uv run --extra dev ruff format --check src tests

typecheck:
	uv run --extra dev pyright

test:
	uv run --extra dev pytest

coverage:
	uv run --extra dev pytest --cov=langgraph_yaml --cov-report=term-missing

build:
	uv build --wheel

wheel-smoke: build
	uv run --extra dev python -c "import langgraph_yaml; print(langgraph_yaml.__version__)"

check: lint typecheck coverage wheel-smoke
