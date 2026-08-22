.PHONY: check lint format typecheck test

check: lint format typecheck test

lint:
	python -m ruff check .

format:
	python -m ruff format --check .

typecheck:
	python -m pyright

test:
	python -m pytest
