from dataclasses import dataclass
from uuid import UUID

from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus


@dataclass(frozen=True, slots=True)
class MembershipAuthorizationInfo:
    business_id: UUID
    user_id: UUID
    role: MembershipRole
    status: MembershipStatus
    branch_access_scope: BranchAccessScope
