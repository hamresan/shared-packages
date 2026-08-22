"""Resource resolver used by FastAPI authorization tests."""

from fastapi import Request

from integration_auth.domain.value_objects.integration_resource import IntegrationResource


class StorePathResourceResolver:
    """Resolve a store resource from a FastAPI path parameter."""

    def __call__(self, request: Request) -> IntegrationResource:
        return IntegrationResource("store", str(request.path_params["store_id"]))
