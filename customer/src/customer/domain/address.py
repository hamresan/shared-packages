from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CustomerAddress:
    id: UUID
    business_id: UUID
    customer_id: UUID
    label: str
    country_code: str
    line1: str
    city: str
    region: str | None
    postal_code: str | None
    is_default: bool
