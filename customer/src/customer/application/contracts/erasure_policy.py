"""Host authority for retention holds and lawful erasure."""

from typing import Protocol
from uuid import UUID

from customer.application.actor import CustomerActor


class CustomerErasurePolicy(Protocol):
    async def require_allowed(
        self, actor: CustomerActor, business_id: UUID, customer_id: UUID
    ) -> None: ...
