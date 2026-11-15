from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.branch_access import BranchBusinessAccess, BranchScopePolicy
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.domain.branch import Branch


class ReactivateBranchService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access: BranchBusinessAccess,
        scope_policy: BranchScopePolicy,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access = access
        self._scope_policy = scope_policy
        self._clock = clock

    async def execute(
        self, business_id: UUID, branch_id: UUID, *, actor: AuthenticatedActor
    ) -> Branch:
        async with self._unit_of_work_factory() as unit_of_work:
            await self._access.require_writable(unit_of_work, business_id, actor)
            branch = self._scope_policy.require_for_business(
                await unit_of_work.branches.get_for_business(business_id, branch_id), business_id
            )
            branch.reactivate(reactivated_at=self._clock.now())
            await unit_of_work.branches.save(branch)
            await unit_of_work.commit()
            return branch
