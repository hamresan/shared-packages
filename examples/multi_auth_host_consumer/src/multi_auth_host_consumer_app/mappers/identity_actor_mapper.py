"""Map human identity principals into the host actor abstraction."""

from identity.public import AuthenticatedPrincipal

from multi_auth_host_consumer_app.actors import HostActor, HostActorKind


class IdentityActorMapper:
    """Translate an authenticated human principal at the host boundary."""

    def map(self, principal: AuthenticatedPrincipal) -> HostActor:
        return HostActor(
            actor_id=f"user:{principal.user_id}",
            kind=HostActorKind.HUMAN,
            authentication_method=principal.authentication_method,
        )
