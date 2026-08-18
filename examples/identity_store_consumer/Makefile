PYTHON ?= python
IMAGE ?= hamresan-identity-store-consumer

.PHONY: lint format-check typecheck test check docker-test

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m pyright

test:
	$(PYTHON) -m pytest

check: lint format-check typecheck test

docker-test:
	docker build -f Dockerfile -t $(IMAGE) ../..
	docker run --rm $(IMAGE)
