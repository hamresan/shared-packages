.PHONY: install-dev check lint format-check typecheck test docker-test

install-dev:
	python -m pip install -e "../../notification"
	python -m pip install -e "../../identity"
	python -m pip install -e ".[test]"

check: lint format-check typecheck test

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

typecheck:
	python -m pyright

test:
	python -m pytest

docker-test:
	docker build -f Dockerfile -t identity-notification-consumer-test ../..
	docker run --rm identity-notification-consumer-test
