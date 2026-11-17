"""Persistence boundary for contact points scoped by business and customer."""

from typing import Protocol
from uuid import UUID

from customer.domain.contact import ContactKind, CustomerContact


class CustomerContactRepository(Protocol):
    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerContact, ...]: ...

    async def get(
        self, business_id: UUID, customer_id: UUID, contact_id: UUID
    ) -> CustomerContact | None: ...

    async def add(self, contact: CustomerContact) -> None: ...

    async def save(self, contact: CustomerContact) -> None: ...

    async def remove(self, business_id: UUID, customer_id: UUID, contact_id: UUID) -> None: ...

    async def unset_primary(
        self, business_id: UUID, customer_id: UUID, kind: ContactKind
    ) -> None: ...
