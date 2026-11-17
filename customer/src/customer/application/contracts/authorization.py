"""Host-resolved Customer operation authorization boundary."""

from typing import Protocol
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.permissions import CustomerPermission


class CustomerAuthorizer(Protocol):
    async def require_permission(
        self,
        actor: CustomerActor,
        permission: CustomerPermission,
        customer_id: UUID | None = None,
    ) -> None: ...
