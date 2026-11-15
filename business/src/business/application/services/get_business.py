from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory
from business.application.policies import BusinessAccessPolicy
from business.domain.business import Business
from business.domain.errors import BusinessNotFoundError


class GetBusinessService:
    def __init__(
        self, unit_of_work_factory: BusinessUnitOfWorkFactory, access_policy: BusinessAccessPolicy
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access_policy = access_policy

    async def execute(self, business_id: UUID, *, actor: AuthenticatedActor) -> Business:
        async with self._unit_of_work_factory() as unit_of_work:
            membership = await unit_of_work.memberships.get_by_business_and_user(
                business_id, actor.user_id
            )
            self._access_policy.require_member(membership)
            business = await unit_of_work.businesses.get_by_id(business_id)
            if business is None:
                raise BusinessNotFoundError("Business was not found")
            return business
