.PHONY: format lint typecheck test coverage check

format:
	ruff format src tests

lint:
	ruff check src tests
	ruff format --check src tests

typecheck:
	pyright

test:
	pytest

coverage:
	pytest

check: lint typecheck coverage
