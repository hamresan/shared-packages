"""Create one authorized tenant-scoped calendar."""

from scheduling.domain.calendar import Calendar
from scheduling.domain.calendar.creation_policy import validate_new_calendar

from ..contracts import CalendarAuthorizer, CalendarUnitOfWorkFactory
from ..errors import CrossTenantCalendarError
from ..models import TrustedActor


class CreateCalendar:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, authorizer: CalendarAuthorizer
    ) -> None:
        self._uow_factory = uow_factory
        self._authorizer = authorizer

    async def execute(self, actor: TrustedActor, calendar: Calendar) -> Calendar:
        if actor.tenant_id != calendar.tenant_id:
            raise CrossTenantCalendarError("Cannot create a calendar in another tenant.")
        validate_new_calendar(calendar)
        await self._authorizer.ensure_can_manage(actor, calendar.scope, calendar.scope_id)
        async with self._uow_factory.create() as uow:
            await uow.calendars.add(calendar)
            await uow.commit()
        return calendar
