"""Create or replace one local-day closure or hours override."""

from scheduling.domain.calendar import Calendar, CalendarException
from scheduling.domain.calendar.revisions import set_date_exception

from ..contracts import CalendarUnitOfWorkFactory
from ..models import TrustedActor
from ..policies import CalendarMutationGuard


class SetDateException:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, guard: CalendarMutationGuard
    ) -> None:
        self._uow_factory = uow_factory
        self._guard = guard

    async def execute(
        self,
        actor: TrustedActor,
        calendar_id: str,
        expected_version: int,
        exception: CalendarException,
    ) -> Calendar:
        async with self._uow_factory.create() as uow:
            original = await self._guard.load(actor, calendar_id, expected_version, uow.calendars)
            revised = set_date_exception(original, exception)
            await uow.calendars.update_if_version(revised, expected_version)
            await uow.commit()
        return revised
