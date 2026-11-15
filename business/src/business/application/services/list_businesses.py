from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory
from business.domain.business import Business
from business.domain.enums import MembershipStatus


class ListBusinessesService:
    def __init__(self, unit_of_work_factory: BusinessUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def execute(self, *, actor: AuthenticatedActor) -> tuple[Business, ...]:
        async with self._unit_of_work_factory() as unit_of_work:
            memberships = await unit_of_work.memberships.list_by_user_id(actor.user_id)
            authorized_ids = tuple(
                membership.business_id
                for membership in memberships
                if membership.status is MembershipStatus.ACTIVE
            )
            if not authorized_ids:
                return ()
            return await unit_of_work.businesses.list_by_ids(authorized_ids)
