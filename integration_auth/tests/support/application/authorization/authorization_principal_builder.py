"""Test builder for authorization principals."""

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


class AuthorizationPrincipalBuilder:
    """Build authenticated principals with explicit grants for authorization tests."""

    def __init__(self) -> None:
        self.client_id = IntegrationClientId("client-123")
        self.permissions: frozenset[Permission] = frozenset()
        self.scopes: frozenset[IntegrationScope] = frozenset()

    def build(self) -> IntegrationPrincipal:
        return IntegrationPrincipal(
            client_id=self.client_id,
            permissions=self.permissions,
            scopes=self.scopes,
        )
