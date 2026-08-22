"""Host-owned composition of human and integration actor mappers."""

from identity.public import AuthenticatedPrincipal
from integration_auth import IntegrationPrincipal

from multi_auth_host_consumer_app.actors import HostActor
from multi_auth_host_consumer_app.mappers import IdentityActorMapper, IntegrationActorMapper


class HostActorFactory:
    """Compose package-specific principals into the host-owned actor abstraction."""

    def __init__(
        self,
        *,
        identity_mapper: IdentityActorMapper,
        integration_mapper: IntegrationActorMapper,
    ) -> None:
        self._identity_mapper = identity_mapper
        self._integration_mapper = integration_mapper

    def from_identity(self, principal: AuthenticatedPrincipal) -> HostActor:
        return self._identity_mapper.map(principal)

    def from_integration(self, principal: IntegrationPrincipal) -> HostActor:
        return self._integration_mapper.map(principal)
