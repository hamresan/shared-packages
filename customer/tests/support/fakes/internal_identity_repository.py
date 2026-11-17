from dataclasses import replace
from uuid import UUID

from customer.application.contracts.internal_identity_repository import (
    CustomerIdentityLinkRepository,
)
from customer.domain.errors import CustomerIdentityConflictError
from customer.domain.identity_link import CustomerIdentityLink


class InMemoryIdentityLinkRepository(CustomerIdentityLinkRepository):
    def __init__(self) -> None:
        self.links: list[CustomerIdentityLink] = []

    async def find_by_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> CustomerIdentityLink | None:
        return next(
            (
                replace(link)
                for link in self.links
                if link.business_id == business_id
                and link.customer_id == customer_id
                and link.is_active
            ),
            None,
        )

    async def find_by_user(
        self, business_id: UUID, identity_user_id: UUID
    ) -> CustomerIdentityLink | None:
        return next(
            (
                replace(link)
                for link in self.links
                if link.business_id == business_id
                and link.identity_user_id == identity_user_id
                and link.is_active
            ),
            None,
        )

    async def add(self, link: CustomerIdentityLink) -> None:
        existing_customer = await self.find_by_customer(link.business_id, link.customer_id)
        existing_user = await self.find_by_user(link.business_id, link.identity_user_id)
        if existing_customer is not None or existing_user is not None:
            raise CustomerIdentityConflictError("Active identity link already exists")
        self.links.append(replace(link))

    async def revoke(self, link: CustomerIdentityLink) -> None:
        for index, previous in enumerate(self.links):
            if previous.id == link.id:
                self.links[index] = replace(link)
                return
