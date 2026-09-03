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
	pytest --cov=instagram_auth --cov-branch --cov-report=term-missing --cov-fail-under=85

check: lint typecheck coverage
