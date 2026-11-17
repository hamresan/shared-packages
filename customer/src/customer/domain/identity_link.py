"""Optional, business-scoped association with a host-managed user identity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class CustomerIdentityLink:
    id: UUID
    business_id: UUID
    customer_id: UUID
    identity_user_id: UUID
    linked_at: datetime
    revoked_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None
