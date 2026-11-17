"""Trusted actor identity, independent of any authentication provider."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class CustomerActorType(StrEnum):
    USER = "user"
    SERVICE = "service"


@dataclass(frozen=True, slots=True)
class CustomerActor:
    """Actor resolved and authenticated by the host, never from raw input."""

    actor_id: UUID
    actor_type: CustomerActorType
    business_id: UUID
