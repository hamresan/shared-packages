"""Host-owned multi-auth composition example."""

from .actors import HostActor, HostActorKind
from .services.actor_description_service import ActorDescriptionService

__all__ = (
    "ActorDescriptionService",
    "HostActor",
    "HostActorKind",
)
