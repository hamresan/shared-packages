from typing import Protocol
from uuid import UUID

from customer.domain.identity_link import CustomerIdentityLink


class CustomerIdentityLinkRepository(Protocol):
    async def find_by_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> CustomerIdentityLink | None: ...

    async def find_by_user(
        self, business_id: UUID, identity_user_id: UUID
    ) -> CustomerIdentityLink | None: ...

    async def add(self, link: CustomerIdentityLink) -> None: ...

    async def revoke(self, link: CustomerIdentityLink) -> None: ...
