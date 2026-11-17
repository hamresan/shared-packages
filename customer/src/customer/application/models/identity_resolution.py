"""Minimal identity lookup projections, never a downstream authorization grant."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from customer.domain.external_identity import ExternalIdentityStatus


@dataclass(frozen=True, slots=True)
class CustomerResolution:
    customer_id: UUID
    business_id: UUID
    identity_status: ExternalIdentityStatus
    verification_method: str
    verified_at: datetime
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class InternalIdentityResolution:
    customer_id: UUID
    business_id: UUID
    identity_user_id: UUID
