from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.policies import BusinessAccessPolicy
from business.domain.business import Business
from business.domain.errors import BusinessNotFoundError


class ArchiveBusinessService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access_policy: BusinessAccessPolicy,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access_policy = access_policy
        self._clock = clock

    async def execute(self, business_id: UUID, *, actor: AuthenticatedActor) -> Business:
        async with self._unit_of_work_factory() as unit_of_work:
            membership = await unit_of_work.memberships.get_by_business_and_user(
                business_id, actor.user_id
            )
            self._access_policy.require_owner(membership)
            business = await unit_of_work.businesses.get_by_id(business_id)
            if business is None:
                raise BusinessNotFoundError("Business was not found")
            business.archive(archived_at=self._clock.now())
            await unit_of_work.businesses.save(business)
            await unit_of_work.commit()
            return business
