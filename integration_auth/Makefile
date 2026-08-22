PYTHON ?= python

.PHONY: install-dev lint format-check typecheck test coverage build wheel-smoke check release-check

install-dev:
	$(PYTHON) -m pip install -e ".[test]"

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m pyright

test:
	$(PYTHON) -m pytest

coverage:
	$(PYTHON) -m pytest

build:
	rm -rf dist
	$(PYTHON) -m build

wheel-smoke: build
	$(PYTHON) scripts/release/wheel_smoke.py

check: lint format-check typecheck coverage build

release-check: lint format-check typecheck coverage wheel-smoke
