from dataclasses import dataclass
from uuid import UUID

PreferenceValue = str | int | bool


@dataclass(frozen=True, slots=True)
class CustomerPreference:
    id: UUID
    business_id: UUID
    customer_id: UUID
    key: str
    value: PreferenceValue
