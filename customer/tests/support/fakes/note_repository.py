from uuid import UUID

from customer.application.contracts.note_repository import CustomerNoteRepository
from customer.domain.note import CustomerNote


class InMemoryNoteRepository(CustomerNoteRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, UUID, UUID], CustomerNote] = {}

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerNote, ...]:
        return tuple(
            value
            for (business, customer, _), value in self.records.items()
            if business == business_id and customer == customer_id
        )

    async def add(self, note: CustomerNote) -> None:
        self.records[(note.business_id, note.customer_id, note.id)] = note

    async def remove(self, business_id: UUID, customer_id: UUID, note_id: UUID) -> bool:
        return self.records.pop((business_id, customer_id, note_id), None) is not None
