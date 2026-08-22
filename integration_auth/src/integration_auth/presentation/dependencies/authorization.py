"""FastAPI permission and resource-scope dependency factory."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request

from integration_auth.application.contracts.authorization.integration_authorizer import (
    IntegrationRequestAuthorizer,
)
from integration_auth.application.errors.authorization import IntegrationAuthorizationError
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.permission import Permission
from integration_auth.presentation.dependencies.authentication import (
    IntegrationAuthenticationDependency,
)
from integration_auth.presentation.errors.http_error_mapper import FastApiIntegrationErrorMapper

ResourceResolver = Callable[[Request], IntegrationResource | None]
AuthorizationDependency = Callable[
    [Request, IntegrationPrincipal],
    Awaitable[IntegrationPrincipal],
]


class IntegrationPermissionDependencyFactory:
    """Build reusable FastAPI dependencies for permission and optional scope enforcement."""

    def __init__(
        self,
        *,
        authorizer: IntegrationRequestAuthorizer,
        authentication_dependency: IntegrationAuthenticationDependency,
        error_mapper: FastApiIntegrationErrorMapper,
    ) -> None:
        self._authorizer = authorizer
        self._authentication_dependency = authentication_dependency
        self._error_mapper = error_mapper

    def create(
        self,
        permission: Permission,
        *,
        resource_resolver: ResourceResolver | None = None,
    ) -> AuthorizationDependency:
        authentication_dependency = self._authentication_dependency
        authorizer = self._authorizer
        error_mapper = self._error_mapper

        async def dependency(
            request: Request,
            principal: Annotated[IntegrationPrincipal, Depends(authentication_dependency)],
        ) -> IntegrationPrincipal:
            resource = None if resource_resolver is None else resource_resolver(request)
            try:
                authorizer.require(
                    principal=principal,
                    permission=permission,
                    resource=resource,
                )
            except IntegrationAuthorizationError as exc:
                raise error_mapper.authorization_error() from exc
            return principal

        return dependency
