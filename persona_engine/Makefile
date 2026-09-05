.PHONY: check lint format-check typecheck test coverage


check: lint format-check typecheck coverage

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

typecheck:
	python -m pyright

test:
	PYTHONPATH=src:../persona_engine/src python -m pytest --no-cov

coverage:
	PYTHONPATH=src:../persona_engine/src python -m pytest
