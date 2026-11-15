from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedActor:
    """Trusted identity resolved by the host authentication boundary."""

    user_id: UUID
