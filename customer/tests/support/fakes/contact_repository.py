from dataclasses import replace
from uuid import UUID

from customer.application.contracts.contact_repository import CustomerContactRepository
from customer.domain.contact import ContactKind, CustomerContact


class InMemoryContactRepository(CustomerContactRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, UUID, UUID], CustomerContact] = {}

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerContact, ...]:
        return tuple(
            replace(value)
            for (scope, owner, _), value in self.records.items()
            if scope == business_id and owner == customer_id
        )

    async def get(
        self, business_id: UUID, customer_id: UUID, contact_id: UUID
    ) -> CustomerContact | None:
        value = self.records.get((business_id, customer_id, contact_id))
        return replace(value) if value is not None else None

    async def add(self, contact: CustomerContact) -> None:
        self.records[(contact.business_id, contact.customer_id, contact.id)] = replace(contact)

    async def save(self, contact: CustomerContact) -> None:
        self.records[(contact.business_id, contact.customer_id, contact.id)] = replace(contact)

    async def remove(self, business_id: UUID, customer_id: UUID, contact_id: UUID) -> None:
        del self.records[(business_id, customer_id, contact_id)]

    async def unset_primary(self, business_id: UUID, customer_id: UUID, kind: ContactKind) -> None:
        for key, contact in self.records.items():
            if key[0] == business_id and key[1] == customer_id and contact.kind == kind:
                contact.is_primary = False
