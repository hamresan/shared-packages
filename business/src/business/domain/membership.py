from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus
from business.domain.errors import MembershipInvalidStateError


@dataclass(slots=True)
class BusinessMembership:
    id: UUID
    business_id: UUID
    user_id: UUID
    role: MembershipRole
    status: MembershipStatus
    created_at: datetime
    updated_at: datetime
    branch_access_scope: BranchAccessScope = BranchAccessScope.ALL

    def accept(self, *, accepted_at: datetime) -> None:
        if self.status is not MembershipStatus.INVITED:
            raise MembershipInvalidStateError("Only invited memberships can be accepted")
        self.status = MembershipStatus.ACTIVE
        self.updated_at = accepted_at

    def change_role(self, role: MembershipRole, *, changed_at: datetime) -> None:
        if self.status is not MembershipStatus.ACTIVE:
            raise MembershipInvalidStateError("Only active members can change roles")
        if self.role is MembershipRole.OWNER or role is MembershipRole.OWNER:
            raise MembershipInvalidStateError(
                "Ownership can only change through ownership transfer"
            )
        if self.role is role:
            raise MembershipInvalidStateError("Membership already has this role")
        self.role = role
        self.branch_access_scope = (
            BranchAccessScope.ALL if role is MembershipRole.MANAGER else BranchAccessScope.SELECTED
        )
        self.updated_at = changed_at

    def relinquish_ownership(self, *, changed_at: datetime) -> None:
        if self.status is not MembershipStatus.ACTIVE or self.role is not MembershipRole.OWNER:
            raise MembershipInvalidStateError("Only an active owner can transfer ownership")
        self.role = MembershipRole.MANAGER
        self.branch_access_scope = BranchAccessScope.ALL
        self.updated_at = changed_at

    def assume_ownership(self, *, changed_at: datetime) -> None:
        if self.status is not MembershipStatus.ACTIVE or self.role is MembershipRole.OWNER:
            raise MembershipInvalidStateError("Only an active non-owner can receive ownership")
        self.role = MembershipRole.OWNER
        self.branch_access_scope = BranchAccessScope.ALL
        self.updated_at = changed_at

    def revoke(self, *, revoked_at: datetime) -> None:
        if self.status is MembershipStatus.REVOKED:
            raise MembershipInvalidStateError("Membership is already revoked")
        self.status = MembershipStatus.REVOKED
        self.branch_access_scope = BranchAccessScope.SELECTED
        self.updated_at = revoked_at

    def change_branch_scope(self, scope: BranchAccessScope, *, changed_at: datetime) -> None:
        if self.status is MembershipStatus.REVOKED:
            raise MembershipInvalidStateError("Revoked memberships cannot access branches")
        if (
            self.role in (MembershipRole.OWNER, MembershipRole.MANAGER)
            and scope is not BranchAccessScope.ALL
        ):
            raise MembershipInvalidStateError("Owners and managers must have full branch access")
        self.branch_access_scope = scope
        self.updated_at = changed_at
