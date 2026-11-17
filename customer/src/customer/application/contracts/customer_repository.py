from typing import Protocol
from uuid import UUID

from customer.domain.customer import Customer


class CustomerRepository(Protocol):
    async def get(self, business_id: UUID, customer_id: UUID) -> Customer | None: ...

    async def add(self, customer: Customer) -> None: ...

    async def save(self, customer: Customer, expected_version: int) -> None: ...

    async def search(
        self, business_id: UUID, name_contains: str | None, offset: int, limit: int
    ) -> tuple[Customer, ...]: ...
