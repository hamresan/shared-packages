from datetime import datetime
from uuid import UUID

from customer.domain.external_identity import (
    CustomerExternalIdentity,
    ExternalIdentityKey,
    ExternalIdentityStatus,
)


class ExternalIdentityFactory:
    def create(
        self,
        identity_id: UUID,
        customer_id: UUID,
        key: ExternalIdentityKey,
        method: str,
        verified_at: datetime,
        linked_at: datetime,
    ) -> CustomerExternalIdentity:
        return CustomerExternalIdentity(
            identity_id,
            key,
            customer_id,
            ExternalIdentityStatus.ACTIVE,
            linked_at,
            method,
            verified_at,
        )
