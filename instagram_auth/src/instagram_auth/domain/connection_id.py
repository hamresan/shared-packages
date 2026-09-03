"""Instagram connection identifier value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class InstagramConnectionId:
    """Package-owned identifier for one independent Instagram connection."""

    value: UUID
