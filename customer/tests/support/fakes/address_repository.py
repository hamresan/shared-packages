from dataclasses import replace
from uuid import UUID

from customer.application.contracts.address_repository import CustomerAddressRepository
from customer.domain.address import CustomerAddress


class InMemoryAddressRepository(CustomerAddressRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, UUID, UUID], CustomerAddress] = {}

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerAddress, ...]:
        return tuple(
            replace(value)
            for (business, customer, _), value in self.records.items()
            if business == business_id and customer == customer_id
        )

    async def get(
        self, business_id: UUID, customer_id: UUID, address_id: UUID
    ) -> CustomerAddress | None:
        value = self.records.get((business_id, customer_id, address_id))
        return replace(value) if value else None

    async def add(self, address: CustomerAddress) -> None:
        self.records[(address.business_id, address.customer_id, address.id)] = replace(address)

    async def save(self, address: CustomerAddress) -> None:
        self.records[(address.business_id, address.customer_id, address.id)] = replace(address)

    async def remove(self, business_id: UUID, customer_id: UUID, address_id: UUID) -> None:
        del self.records[(business_id, customer_id, address_id)]

    async def unset_default(self, business_id: UUID, customer_id: UUID) -> None:
        for (business, customer, _), address in self.records.items():
            if business == business_id and customer == customer_id:
                address.is_default = False
