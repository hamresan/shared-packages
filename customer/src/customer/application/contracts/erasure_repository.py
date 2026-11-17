"""Storage boundary for removing all customer-owned child information."""

from typing import Protocol
from uuid import UUID


class CustomerErasureRepository(Protocol):
    async def erase_children(self, business_id: UUID, customer_id: UUID) -> None: ...
