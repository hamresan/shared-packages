.PHONY: install-dev check lint format-check typecheck test coverage package-build

install-dev:
	python -m pip install -e ".[test]"

check: lint format-check typecheck coverage package-build

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

package-build:
	rm -rf dist
	python -m build
