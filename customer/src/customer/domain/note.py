from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CustomerNote:
    id: UUID
    business_id: UUID
    customer_id: UUID
    author_id: UUID
    author_type: str
    body: str
    created_at: datetime
