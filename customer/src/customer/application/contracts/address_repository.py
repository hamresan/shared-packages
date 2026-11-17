from typing import Protocol
from uuid import UUID

from customer.domain.address import CustomerAddress


class CustomerAddressRepository(Protocol):
    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerAddress, ...]: ...

    async def get(
        self, business_id: UUID, customer_id: UUID, address_id: UUID
    ) -> CustomerAddress | None: ...

    async def add(self, address: CustomerAddress) -> None: ...

    async def save(self, address: CustomerAddress) -> None: ...

    async def remove(self, business_id: UUID, customer_id: UUID, address_id: UUID) -> None: ...

    async def unset_default(self, business_id: UUID, customer_id: UUID) -> None: ...
