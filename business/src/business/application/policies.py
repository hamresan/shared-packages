from business.domain.enums import MembershipRole, MembershipStatus
from business.domain.errors import BusinessNotFoundError, BusinessPermissionDeniedError
from business.domain.membership import BusinessMembership


class BusinessAccessPolicy:
    def require_member(self, membership: BusinessMembership | None) -> BusinessMembership:
        if membership is None or membership.status is not MembershipStatus.ACTIVE:
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
