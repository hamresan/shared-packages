PYTHON ?= python

.PHONY: install-dev lint format-check typecheck test coverage build check

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
	$(PYTHON) -m build

check: lint format-check typecheck coverage build
