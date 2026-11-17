"""Host-provided verification of an internal identity reference."""

from typing import Protocol
from uuid import UUID


class IdentityVerifier(Protocol):
    async def require_valid_user(self, identity_user_id: UUID) -> None: ...
