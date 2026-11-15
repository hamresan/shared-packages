from business.application.actor import AuthenticatedActor
from business.application.branch_access import BranchBusinessAccess, BranchScopePolicy
from business.application.branch_validators import UpdateBranchCommandValidator
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto import UpdateBranchCommand
from business.domain.branch import Branch


class UpdateBranchService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access: BranchBusinessAccess,
        scope_policy: BranchScopePolicy,
        validator: UpdateBranchCommandValidator,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access = access
        self._scope_policy = scope_policy
        self._validator = validator
        self._clock = clock

    async def execute(self, command: UpdateBranchCommand, *, actor: AuthenticatedActor) -> Branch:
        async with self._unit_of_work_factory() as unit_of_work:
            await self._access.require_writable(unit_of_work, command.business_id, actor)
            branch = self._scope_policy.require_for_business(
                await unit_of_work.branches.get_for_business(
                    command.business_id, command.branch_id
                ),
                command.business_id,
            )
            validated = self._validator.validate(command)
            branch.update_details(
                name=validated.name,
                timezone=validated.timezone,
                address=validated.address,
                contact=validated.contact,
                updated_at=self._clock.now(),
            )
            await unit_of_work.branches.save(branch)
            await unit_of_work.commit()
            return branch
