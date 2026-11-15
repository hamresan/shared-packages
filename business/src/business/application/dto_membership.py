from dataclasses import dataclass
from uuid import UUID

from business.domain.enums import BranchAccessScope, MembershipRole


@dataclass(frozen=True, slots=True)
class InviteMemberCommand:
    business_id: UUID
    user_id: UUID


@dataclass(frozen=True, slots=True)
class ChangeMemberRoleCommand:
    business_id: UUID
    membership_id: UUID
    role: MembershipRole


@dataclass(frozen=True, slots=True)
class SetMemberBranchAccessCommand:
    business_id: UUID
    membership_id: UUID
    scope: BranchAccessScope
    branch_ids: tuple[UUID, ...] = ()
