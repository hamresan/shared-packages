"""Map authenticated client data to an integration principal."""

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal


class IntegrationPrincipalMapper:
    """Create an immutable authentication principal from client grants."""

    def from_client(self, client: IntegrationClient) -> IntegrationPrincipal:
        return IntegrationPrincipal(
            client_id=client.client_id,
            permissions=client.permissions,
            scopes=client.scopes,
        )
