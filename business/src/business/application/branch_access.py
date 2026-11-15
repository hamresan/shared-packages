from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWork
from business.application.policies import BusinessAccessPolicy
from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.enums import BusinessStatus
from business.domain.errors import (
    BranchNotFoundError,
    BusinessArchivedError,
    BusinessNotFoundError,
)


class BranchBusinessAccess:
    def __init__(self, membership_policy: BusinessAccessPolicy) -> None:
        self._membership_policy = membership_policy

    async def require_readable(
        self, unit_of_work: BusinessUnitOfWork, business_id: UUID, actor: AuthenticatedActor
    ) -> Business:
        membership = await unit_of_work.memberships.get_by_business_and_user(
            business_id, actor.user_id
        )
        self._membership_policy.require_member(membership)
        return await self._get_business(unit_of_work, business_id)

    async def require_writable(
        self, unit_of_work: BusinessUnitOfWork, business_id: UUID, actor: AuthenticatedActor
    ) -> Business:
        membership = await unit_of_work.memberships.get_by_business_and_user(
            business_id, actor.user_id
        )
        self._membership_policy.require_owner(membership)
        business = await self._get_business(unit_of_work, business_id)
        if business.status is BusinessStatus.ARCHIVED:
            raise BusinessArchivedError("Archived businesses cannot change branches")
        return business

    async def _get_business(self, unit_of_work: BusinessUnitOfWork, business_id: UUID) -> Business:
        business = await unit_of_work.businesses.get_by_id(business_id)
        if business is None:
            raise BusinessNotFoundError("Business was not found")
        return business


class BranchScopePolicy:
    def require_for_business(self, branch: Branch | None, business_id: UUID) -> Branch:
        if branch is None or branch.business_id != business_id:
            raise BranchNotFoundError("Branch was not found")
        return branch
