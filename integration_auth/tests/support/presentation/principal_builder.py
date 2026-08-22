"""Integration principal builder for presentation tests."""

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


class IntegrationPrincipalBuilder:
    """Build integration principals for FastAPI presentation scenarios."""

    def __init__(self) -> None:
        self._client_id = IntegrationClientId("client-123")
        self._permissions: frozenset[Permission] = frozenset({Permission("orders.read")})
        self._scopes: frozenset[IntegrationScope] = frozenset(
            {IntegrationScope("store", "store-123")}
        )

    def build(self) -> IntegrationPrincipal:
        return IntegrationPrincipal(
            client_id=self._client_id,
            permissions=self._permissions,
            scopes=self._scopes,
        )
