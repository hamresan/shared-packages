from dataclasses import replace
from uuid import UUID

from customer.application.contracts.external_identity_repository import (
    CustomerExternalIdentityRepository,
)
from customer.domain.errors import CustomerIdentityConflictError
from customer.domain.external_identity import (
    CustomerExternalIdentity,
    ExternalIdentityKey,
    ExternalIdentityStatus,
)


class InMemoryExternalIdentityRepository(CustomerExternalIdentityRepository):
    def __init__(self) -> None:
        self.identities: list[CustomerExternalIdentity] = []

    async def find_active(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None:
        return next(
            (
                replace(item)
                for item in self.identities
                if item.key == key and item.status is ExternalIdentityStatus.ACTIVE
            ),
            None,
        )

    async def find_latest(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None:
        return next((replace(item) for item in reversed(self.identities) if item.key == key), None)

    async def get_active_for_customer(
        self, key: ExternalIdentityKey, customer_id: UUID
    ) -> CustomerExternalIdentity | None:
        identity = await self.find_active(key)
        return identity if identity is not None and identity.customer_id == customer_id else None

    async def add(self, identity: CustomerExternalIdentity) -> None:
        if await self.find_active(identity.key):
            raise CustomerIdentityConflictError("External identity already active")
        self.identities.append(replace(identity))

    async def save(self, identity: CustomerExternalIdentity) -> None:
        for index, item in enumerate(self.identities):
            if item.id == identity.id:
                self.identities[index] = replace(identity)
                return
