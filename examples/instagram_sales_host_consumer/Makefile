.PHONY: lint format-check typecheck test check

lint:
	ruff check src tests

format-check:
	ruff format --check src tests

typecheck:
	pyright

test:
	pytest

check: lint format-check typecheck test
