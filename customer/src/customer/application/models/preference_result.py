from dataclasses import dataclass
from uuid import UUID

from customer.domain.preference import PreferenceValue


@dataclass(frozen=True, slots=True)
class PreferenceResult:
    id: UUID
    business_id: UUID
    customer_id: UUID
    key: str
    value: PreferenceValue
