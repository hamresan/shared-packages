"""Customer-owned contact point; verification is never inferred from its value."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ContactKind(StrEnum):
    EMAIL = "email"
    PHONE = "phone"


@dataclass(slots=True)
class CustomerContact:
    id: UUID
    business_id: UUID
    customer_id: UUID
    kind: ContactKind
    value: str
    is_primary: bool
    created_at: datetime
    verified_at: datetime | None = None
    verification_method: str | None = None

    def change_value(self, value: str) -> None:
        """Changing a contact invalidates any verification of its old value."""
        self.value = value
        self.verified_at = None
        self.verification_method = None

    def make_primary(self) -> None:
        self.is_primary = True
