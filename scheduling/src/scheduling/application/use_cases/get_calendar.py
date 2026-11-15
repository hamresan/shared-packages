"""Read a calendar within a trusted tenant and authorized scope."""

from scheduling.domain.calendar import Calendar

from ..contracts import CalendarAuthorizer, CalendarUnitOfWorkFactory
from ..errors import CalendarNotFoundError
from ..models import TrustedActor


class GetCalendar:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, authorizer: CalendarAuthorizer
    ) -> None:
        self._uow_factory = uow_factory
        self._authorizer = authorizer

    async def execute(self, actor: TrustedActor, calendar_id: str) -> Calendar:
        async with self._uow_factory.create() as uow:
            calendar = await uow.calendars.get(actor.tenant_id, calendar_id)
            if calendar is None:
                raise CalendarNotFoundError("Calendar not found in the trusted tenant.")
            await self._authorizer.ensure_can_read(actor, calendar.scope, calendar.scope_id)
        return calendar
