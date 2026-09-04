.PHONY: format lint typecheck test coverage build wheel-smoke check

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

build:
	python -m build --wheel

wheel-smoke: build
	rm -rf .wheel-smoke
	python -m venv .wheel-smoke
	.wheel-smoke/bin/python -m pip install dist/hamresan_instagram_api-*.whl
	.wheel-smoke/bin/python -c "import instagram_api; import instagram_api.domain; import instagram_api.application.contracts"
	rm -rf .wheel-smoke

check: lint typecheck coverage wheel-smoke
