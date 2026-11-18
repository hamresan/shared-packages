from business.application.authorization.dto import MembershipAuthorizationInfo
from business.domain.membership import BusinessMembership


class MembershipAuthorizationMapper:
    def to_info(self, membership: BusinessMembership) -> MembershipAuthorizationInfo:
        return MembershipAuthorizationInfo(
            business_id=membership.business_id,
            user_id=membership.user_id,
            role=membership.role,
            status=membership.status,
            branch_access_scope=membership.branch_access_scope,
        )
