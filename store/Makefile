.PHONY: install-dev check lint format-check typecheck test coverage

install-dev:
	python -m pip install -e ".[test]"

check: lint format-check typecheck coverage

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

typecheck:
	python -m pyright

test:
	PYTHONPATH=src python -m pytest --no-cov

coverage:
	PYTHONPATH=src python -m pytest
