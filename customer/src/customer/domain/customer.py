"""Business-owned customer aggregate."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from customer.domain.errors import CustomerErasedError, CustomerInvalidStateError


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    ERASED = "erased"


@dataclass(slots=True)
class Customer:
    id: UUID
    business_id: UUID
    display_name: str | None
    status: CustomerStatus
    version: int
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    erased_at: datetime | None = None

    def update_profile(self, display_name: str | None, changed_at: datetime) -> None:
        self.require_active()
        self.display_name = display_name
        self.version += 1
        self.updated_at = changed_at

    def archive(self, changed_at: datetime) -> None:
        self.require_active()
        self.status = CustomerStatus.ARCHIVED
        self.archived_at = changed_at
        self.updated_at = changed_at
        self.version += 1

    def reactivate(self, changed_at: datetime) -> None:
        if self.status is CustomerStatus.ERASED:
            raise CustomerErasedError("An erased customer cannot be reactivated")
        if self.status is not CustomerStatus.ARCHIVED:
            raise CustomerInvalidStateError("Only archived customers can be reactivated")
        self.status = CustomerStatus.ACTIVE
        self.archived_at = None
        self.updated_at = changed_at
        self.version += 1

    def require_active(self) -> None:
        if self.status is CustomerStatus.ERASED:
            raise CustomerErasedError("An erased customer cannot be modified")
        if self.status is not CustomerStatus.ACTIVE:
            raise CustomerInvalidStateError("Customer is not active")
