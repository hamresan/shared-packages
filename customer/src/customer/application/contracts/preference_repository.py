from typing import Protocol
from uuid import UUID

from customer.domain.preference import CustomerPreference


class CustomerPreferenceRepository(Protocol):
    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerPreference, ...]: ...

    async def get(
        self, business_id: UUID, customer_id: UUID, key: str
    ) -> CustomerPreference | None: ...

    async def upsert(self, preference: CustomerPreference) -> None: ...

    async def remove(self, business_id: UUID, customer_id: UUID, key: str) -> None: ...
