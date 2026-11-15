from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWork
from business.application.policies import BusinessAccessPolicy
from business.domain.enums import BranchAccessScope, BusinessStatus, MembershipRole
from business.domain.errors import BusinessArchivedError, BusinessNotFoundError
from business.domain.membership import BusinessMembership


class MembershipManagementAccess:
    def __init__(self, policy: BusinessAccessPolicy) -> None:
        self._policy = policy

    async def require_owner(
        self, uow: BusinessUnitOfWork, business_id: UUID, actor: AuthenticatedActor
    ) -> None:
        membership = await uow.memberships.get_by_business_and_user(business_id, actor.user_id)
        self._policy.require_owner(membership)
        business = await uow.businesses.get_by_id(business_id)
        if business is None:
            raise BusinessNotFoundError("Business was not found")
        if business.status is BusinessStatus.ARCHIVED:
            raise BusinessArchivedError("Archived businesses cannot change memberships")


class MembershipBranchVisibility:
    async def allowed_ids(
        self, uow: BusinessUnitOfWork, membership: BusinessMembership
    ) -> tuple[UUID, ...] | None:
        if (
            membership.role is MembershipRole.OWNER
            or membership.branch_access_scope is BranchAccessScope.ALL
        ):
            return None
        return await uow.membership_branch_access.list_branch_ids(membership.id)
