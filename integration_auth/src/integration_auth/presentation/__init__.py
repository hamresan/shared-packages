"""FastAPI presentation adapter public API."""

from integration_auth.presentation.dependencies.authentication import (
    IntegrationAuthenticationDependency,
)
from integration_auth.presentation.dependencies.authorization import (
    AuthorizationDependency,
    IntegrationPermissionDependencyFactory,
    ResourceResolver,
)
from integration_auth.presentation.factory import (
    FastApiIntegrationAuth,
    FastApiIntegrationAuthFactory,
)

__all__ = (
    "AuthorizationDependency",
    "FastApiIntegrationAuth",
    "FastApiIntegrationAuthFactory",
    "IntegrationAuthenticationDependency",
    "IntegrationPermissionDependencyFactory",
    "ResourceResolver",
)
