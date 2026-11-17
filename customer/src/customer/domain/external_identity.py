"""Provider-account-scoped external identity; active links only resolve customers."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from customer.domain.errors import CustomerIdentityVerificationError, CustomerInvalidStateError


class ExternalIdentityStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class ExternalIdentityKey:
    business_id: UUID
    provider: str
    channel_account_id: str
    external_user_id: str


@dataclass(slots=True)
class CustomerExternalIdentity:
    id: UUID
    key: ExternalIdentityKey
    customer_id: UUID
    status: ExternalIdentityStatus
    linked_at: datetime
    verification_method: str
    verified_at: datetime
    revoked_at: datetime | None = None

    def revoke(self, at: datetime) -> None:
        if self.status is not ExternalIdentityStatus.ACTIVE:
            raise CustomerInvalidStateError("External identity already revoked")
        self.status = ExternalIdentityStatus.REVOKED
        self.revoked_at = at

    def record_verification(self, method: str, verified_at: datetime) -> None:
        if self.status is not ExternalIdentityStatus.ACTIVE:
            raise CustomerInvalidStateError("Revoked identity cannot be reverified")
        if verified_at < self.verified_at:
            raise CustomerIdentityVerificationError("Verification time cannot move backward")
        self.verification_method = method
        self.verified_at = verified_at
