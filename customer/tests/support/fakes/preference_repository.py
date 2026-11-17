from uuid import UUID

from customer.application.contracts.preference_repository import CustomerPreferenceRepository
from customer.domain.preference import CustomerPreference


class InMemoryPreferenceRepository(CustomerPreferenceRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, UUID, str], CustomerPreference] = {}

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerPreference, ...]:
        return tuple(
            value
            for (business, customer, _), value in self.records.items()
            if business == business_id and customer == customer_id
        )

    async def get(
        self, business_id: UUID, customer_id: UUID, key: str
    ) -> CustomerPreference | None:
        return self.records.get((business_id, customer_id, key))

    async def upsert(self, preference: CustomerPreference) -> None:
        self.records[(preference.business_id, preference.customer_id, preference.key)] = preference

    async def remove(self, business_id: UUID, customer_id: UUID, key: str) -> None:
        del self.records[(business_id, customer_id, key)]
