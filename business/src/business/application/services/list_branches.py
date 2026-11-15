from business.application.actor import AuthenticatedActor
from business.application.branch_access import BranchBusinessAccess
from business.application.branch_validators import ListBranchesQueryValidator
from business.application.contracts import BusinessUnitOfWorkFactory
from business.application.dto import ListBranchesQuery
from business.domain.branch import Branch


class ListBranchesService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access: BranchBusinessAccess,
        validator: ListBranchesQueryValidator,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access = access
        self._validator = validator

    async def execute(
        self, query: ListBranchesQuery, *, actor: AuthenticatedActor
    ) -> tuple[Branch, ...]:
        async with self._unit_of_work_factory() as unit_of_work:
            await self._access.require_readable(unit_of_work, query.business_id, actor)
            validated = self._validator.validate(query)
            return await unit_of_work.branches.list_for_business(
                validated.business_id,
                city=validated.city,
                country_code=validated.country_code,
            )
