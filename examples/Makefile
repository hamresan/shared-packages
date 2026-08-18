.PHONY: check typecheck test coverage

check: typecheck test

typecheck:
	python -m pyright --project ../pyrightconfig.json

test:
	python -m pytest --no-cov

coverage: test
