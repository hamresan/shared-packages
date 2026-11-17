from dataclasses import replace
from uuid import UUID

from customer.application.contracts import CustomerRepository
from customer.domain import Customer, CustomerVersionConflictError


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, UUID], Customer] = {}

    async def get(self, business_id: UUID, customer_id: UUID) -> Customer | None:
        customer = self.records.get((business_id, customer_id))
        return replace(customer) if customer is not None else None

    async def add(self, customer: Customer) -> None:
        self.records[(customer.business_id, customer.id)] = replace(customer)

    async def save(self, customer: Customer, expected_version: int) -> None:
        previous = self.records.get((customer.business_id, customer.id))
        if previous is None or previous.version != expected_version:
            raise CustomerVersionConflictError("Customer version has changed")
        self.records[(customer.business_id, customer.id)] = replace(customer)

    async def search(
        self, business_id: UUID, name_contains: str | None, offset: int, limit: int
    ) -> tuple[Customer, ...]:
        needle = name_contains.casefold().strip() if name_contains is not None else None
        customers = [
            item
            for (scope, _), item in self.records.items()
            if scope == business_id
            and (needle is None or needle in (item.display_name or "").casefold())
        ]
        customers.sort(key=lambda item: (item.created_at, str(item.id)))
        return tuple(replace(item) for item in customers[offset : offset + limit])
