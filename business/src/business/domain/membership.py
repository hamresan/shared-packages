from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business.domain.enums import MembershipRole, MembershipStatus


@dataclass(slots=True)
class BusinessMembership:
    id: UUID
    business_id: UUID
    user_id: UUID
    role: MembershipRole
    status: MembershipStatus
    created_at: datetime
    updated_at: datetime
