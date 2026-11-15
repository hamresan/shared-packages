"""List only calendars in an explicitly authorized scope."""

from scheduling.domain.calendar import Calendar, CalendarScope

from ..contracts import CalendarAuthorizer, CalendarUnitOfWorkFactory
from ..models import TrustedActor


class ListCalendars:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, authorizer: CalendarAuthorizer
    ) -> None:
        self._uow_factory = uow_factory
        self._authorizer = authorizer

    async def execute(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> tuple[Calendar, ...]:
        await self._authorizer.ensure_can_read(actor, scope, scope_id)
        async with self._uow_factory.create() as uow:
            return await uow.calendars.list_by_scope(actor.tenant_id, scope, scope_id)
