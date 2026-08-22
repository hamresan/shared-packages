"""Example downstream service that depends only on the host actor abstraction."""

from multi_auth_host_consumer_app.actors import HostActor


class ActorDescriptionService:
    """Demonstrate business code remaining independent of authentication packages."""

    def describe(self, actor: HostActor) -> dict[str, object]:
        return {
            "actor_id": actor.actor_id,
            "kind": actor.kind.value,
            "authentication_method": actor.authentication_method,
            "permissions": sorted(actor.permissions),
            "resource_scopes": sorted(actor.resource_scopes),
        }
