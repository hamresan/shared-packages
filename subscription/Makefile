.PHONY: install-dev check lint format-check typecheck test coverage package-build package-smoke

install-dev:
	python -m pip install -e ".[test]"

check: lint format-check typecheck coverage package-build package-smoke

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

package-smoke:
	rm -rf .package-smoke
	python -m pip install --no-deps --target .package-smoke dist/*.whl
	PYTHONPATH=.package-smoke python -c "import subscription; from subscription.application import CreatePlanService; from subscription.infrastructure.persistence import build_sqlalchemy_subscription_unit_of_work_factory; from subscription.presentation import FastApiSubscriptionAdapter"
	rm -rf .package-smoke
