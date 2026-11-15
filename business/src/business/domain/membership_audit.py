from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business.domain.enums import MembershipAuditAction


@dataclass(frozen=True, slots=True)
class MembershipAuditRecord:
    id: UUID
    business_id: UUID
    membership_id: UUID
    actor_user_id: UUID
    action: MembershipAuditAction
    occurred_at: datetime
    previous_value: str | None = None
    new_value: str | None = None
    branch_ids: tuple[UUID, ...] = ()
