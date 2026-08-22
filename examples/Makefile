.PHONY: check typecheck test coverage

check: typecheck test

typecheck:
	cd identity_notification_consumer && python -m pyright --project pyrightconfig.json
	cd identity_store_consumer && python -m pyright --project pyrightconfig.json
	cd multi_auth_host_consumer && python -m pyright

test:
	python -m pytest --no-cov

coverage: test
