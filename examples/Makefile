.PHONY: check typecheck test coverage

check: typecheck test

typecheck:
	cd identity_notification_consumer && python -m pyright --project pyrightconfig.json
	cd identity_store_consumer && python -m pyright --project pyrightconfig.json

test:
	python -m pytest --no-cov

coverage: test
