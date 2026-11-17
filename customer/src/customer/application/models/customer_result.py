"""Stable projection returned by Customer use cases."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from customer.domain.customer import CustomerStatus


@dataclass(frozen=True, slots=True)
class CustomerResult:
    id: UUID
    business_id: UUID
    display_name: str | None
    status: CustomerStatus
    version: int
    created_at: datetime
    updated_at: datetime
