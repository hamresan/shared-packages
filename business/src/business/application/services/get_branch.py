from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.branch_access import BranchBusinessAccess, BranchScopePolicy
from business.application.contracts import BusinessUnitOfWorkFactory
from business.domain.branch import Branch


class GetBranchService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access: BranchBusinessAccess,
        scope_policy: BranchScopePolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access = access
        self._scope_policy = scope_policy

    async def execute(
        self, business_id: UUID, branch_id: UUID, *, actor: AuthenticatedActor
    ) -> Branch:
        async with self._unit_of_work_factory() as unit_of_work:
            await self._access.require_readable(unit_of_work, business_id, actor)
            branch = await unit_of_work.branches.get_for_business(business_id, branch_id)
            return self._scope_policy.require_for_business(branch, business_id)
