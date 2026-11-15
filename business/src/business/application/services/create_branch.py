from business.application.actor import AuthenticatedActor
from business.application.branch_access import BranchBusinessAccess
from business.application.branch_validators import CreateBranchCommandValidator
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto import CreateBranchCommand
from business.application.factories import BranchFactory
from business.domain.branch import Branch


class CreateBranchService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access: BranchBusinessAccess,
        validator: CreateBranchCommandValidator,
        factory: BranchFactory,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access = access
        self._validator = validator
        self._factory = factory
        self._clock = clock

    async def execute(self, command: CreateBranchCommand, *, actor: AuthenticatedActor) -> Branch:
        async with self._unit_of_work_factory() as unit_of_work:
            await self._access.require_writable(unit_of_work, command.business_id, actor)
            validated = self._validator.validate(command)
            branch = self._factory.create(validated, created_at=self._clock.now())
            await unit_of_work.branches.add(branch)
            await unit_of_work.commit()
            return branch
