from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory
from business.application.membership_access import MembershipManagementAccess
from business.domain.membership import BusinessMembership


class ListMembershipsService:
    def __init__(
        self, uow_factory: BusinessUnitOfWorkFactory, access: MembershipManagementAccess
    ) -> None:
        self._uow_factory = uow_factory
        self._access = access

    async def execute(
        self, business_id: UUID, *, actor: AuthenticatedActor
    ) -> tuple[BusinessMembership, ...]:
        async with self._uow_factory() as uow:
            await self._access.require_owner(uow, business_id, actor)
            return await uow.memberships.list_for_business(business_id)
