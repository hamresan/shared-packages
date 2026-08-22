"""Public integration-auth domain value objects."""

from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission

__all__ = (
    "IntegrationClientId",
    "IntegrationCredentialId",
    "IntegrationResource",
    "IntegrationScope",
    "Permission",
)
