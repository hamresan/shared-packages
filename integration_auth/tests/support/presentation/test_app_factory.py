"""FastAPI application factory for presentation dependency tests."""

from typing import Annotated

from fastapi import Depends, FastAPI

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.presentation.dependencies.authentication import (
    IntegrationAuthenticationDependency,
)
from integration_auth.presentation.dependencies.authorization import AuthorizationDependency


class FastApiTestAppFactory:
    """Build small FastAPI applications around integration-auth dependencies."""

    def with_authentication(
        self,
        dependency: IntegrationAuthenticationDependency,
        *,
        path: str = "/protected",
        method: str = "GET",
    ) -> FastAPI:
        app = FastAPI()

        async def endpoint(
            authenticated: Annotated[IntegrationPrincipal, Depends(dependency)],
        ) -> dict[str, str]:
            return {"client_id": authenticated.client_id.value}

        app.add_api_route(path, endpoint, methods=[method])
        return app

    def with_authorization(
        self,
        dependency: AuthorizationDependency,
        *,
        path: str,
    ) -> FastAPI:
        app = FastAPI()

        async def endpoint(
            authenticated: Annotated[IntegrationPrincipal, Depends(dependency)],
        ) -> dict[str, str]:
            return {"client_id": authenticated.client_id.value}

        app.add_api_route(path, endpoint, methods=["GET"])
        return app
