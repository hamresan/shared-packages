from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus


class InviteMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID


class ChangeMemberRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: MembershipRole


class SetMemberBranchAccessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scope: BranchAccessScope
    branch_ids: tuple[UUID, ...] = ()


class TransferOwnershipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recipient_membership_id: UUID


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    business_id: UUID
    user_id: UUID
    role: MembershipRole
    status: MembershipStatus
    branch_access_scope: BranchAccessScope
    created_at: datetime
    updated_at: datetime
