"""Host-provided verification of an internal identity reference."""

from typing import Protocol
from uuid import UUID

from customer.application.actor import CustomerActor


class IdentityVerifier(Protocol):
    async def require_linkable_user(
        self, identity_user_id: UUID, actor: CustomerActor, customer_id: UUID
    ) -> None:
        """Host must validate identity existence and authorization for this exact association."""
        ...
