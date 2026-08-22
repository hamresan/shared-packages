PYTHON ?= python

.PHONY: lint format-check typecheck test check

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m pyright

test:
	$(PYTHON) -m pytest

check: lint format-check typecheck test
