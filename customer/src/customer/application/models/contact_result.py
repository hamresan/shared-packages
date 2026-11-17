from dataclasses import dataclass
from uuid import UUID

from customer.domain.contact import ContactKind


@dataclass(frozen=True, slots=True)
class ContactResult:
    id: UUID
    business_id: UUID
    customer_id: UUID
    kind: ContactKind
    value: str
    is_primary: bool
    is_verified: bool
