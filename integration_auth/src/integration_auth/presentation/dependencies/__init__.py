"""FastAPI authentication and authorization dependencies."""

from .authentication import IntegrationAuthenticationDependency
from .authorization import (
    AuthorizationDependency,
    IntegrationPermissionDependencyFactory,
    ResourceResolver,
)

__all__ = (
    "AuthorizationDependency",
    "IntegrationAuthenticationDependency",
    "IntegrationPermissionDependencyFactory",
    "ResourceResolver",
)
