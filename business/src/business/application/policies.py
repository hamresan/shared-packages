from business.domain.enums import MembershipRole, MembershipStatus
from business.domain.errors import BusinessNotFoundError, BusinessPermissionDeniedError
from business.domain.membership import BusinessMembership


class BusinessAccessPolicy:
    def is_active_member(self, membership: BusinessMembership | None) -> bool:
        return membership is not None and membership.status is MembershipStatus.ACTIVE

    def has_any_role(
        self, membership: BusinessMembership | None, allowed_roles: frozenset[MembershipRole]
    ) -> bool:
        return (
            membership is not None
            and self.is_active_member(membership)
            and membership.role in allowed_roles
        )

    def require_member(self, membership: BusinessMembership | None) -> BusinessMembership:
        if membership is None or not self.is_active_member(membership):
            raise BusinessNotFoundError("Business was not found")
        return membership

    def require_owner(self, membership: BusinessMembership | None) -> None:
        active_membership = self.require_member(membership)
        if active_membership.role is not MembershipRole.OWNER:
            raise BusinessPermissionDeniedError("Owner membership is required")

    def require_manager(self, membership: BusinessMembership | None) -> None:
        active_membership = self.require_member(membership)
        if active_membership.role not in (MembershipRole.OWNER, MembershipRole.MANAGER):
            raise BusinessPermissionDeniedError("Owner or manager membership is required")
