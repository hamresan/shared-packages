"""Host-owned actor abstraction independent of authentication packages."""

from dataclasses import dataclass
from enum import StrEnum


class HostActorKind(StrEnum):
    """Authentication-neutral actor categories understood by the host."""

    HUMAN = "human"
    INTEGRATION = "integration"


@dataclass(frozen=True, slots=True)
class HostActor:
    """Host application actor used by downstream business services."""

    actor_id: str
    kind: HostActorKind
    authentication_method: str
    permissions: frozenset[str] = frozenset()
    resource_scopes: frozenset[str] = frozenset()
