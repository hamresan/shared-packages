"""Map machine integration principals into the host actor abstraction."""

from integration_auth import IntegrationPrincipal

from multi_auth_host_consumer_app.actors import HostActor, HostActorKind


class IntegrationActorMapper:
    """Translate an authenticated integration principal at the host boundary."""

    def map(self, principal: IntegrationPrincipal) -> HostActor:
        return HostActor(
            actor_id=f"integration:{principal.client_id.value}",
            kind=HostActorKind.INTEGRATION,
            authentication_method="hmac-sha256",
            permissions=frozenset(permission.value for permission in principal.permissions),
            resource_scopes=frozenset(scope.value for scope in principal.scopes),
        )
