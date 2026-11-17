from typing import Protocol
from uuid import UUID

from customer.domain.note import CustomerNote


class CustomerNoteRepository(Protocol):
    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerNote, ...]: ...

    async def add(self, note: CustomerNote) -> None: ...

    async def remove(self, business_id: UUID, customer_id: UUID, note_id: UUID) -> bool: ...
