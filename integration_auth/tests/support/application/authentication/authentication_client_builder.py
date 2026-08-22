"""Builder for authenticated integration-client test fixtures."""

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


class AuthenticationClientBuilder:
    """Build an integration client with representative authorization grants."""

    def __init__(self) -> None:
        self.client_id = IntegrationClientId("client-123")
        self.permissions = frozenset({Permission("orders.read")})
        self.scopes = frozenset({IntegrationScope("store", "store-123")})

    def build(self) -> IntegrationClient:
        return IntegrationClient(
            client_id=self.client_id,
            permissions=self.permissions,
            scopes=self.scopes,
        )
