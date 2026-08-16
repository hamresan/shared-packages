.PHONY: install-dev check lint format-check typecheck test coverage

install-dev:
	python -m pip install -e "../notification"
	python -m pip install -e ".[test,migrations]"

check: lint format-check typecheck coverage

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

typecheck:
	python -m pyright

test:
	PYTHONPATH=src:../notification/src python -m pytest --no-cov

coverage:
	PYTHONPATH=src:../notification/src python -m pytest
