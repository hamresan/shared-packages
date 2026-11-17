from typing import Protocol
from uuid import UUID

from customer.domain.external_identity import CustomerExternalIdentity, ExternalIdentityKey


class CustomerExternalIdentityRepository(Protocol):
    async def find_active(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None: ...

    async def find_latest(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None: ...

    async def get_active_for_customer(
        self, key: ExternalIdentityKey, customer_id: UUID
    ) -> CustomerExternalIdentity | None: ...

    async def add(self, identity: CustomerExternalIdentity) -> None: ...

    async def save(self, identity: CustomerExternalIdentity) -> None: ...
