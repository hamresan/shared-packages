"""Remove one previously configured date exception."""

from datetime import date

from scheduling.domain.calendar import Calendar
from scheduling.domain.calendar.revisions import remove_date_exception

from ..contracts import CalendarUnitOfWorkFactory
from ..models import TrustedActor
from ..policies import CalendarMutationGuard


class RemoveDateException:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, guard: CalendarMutationGuard
    ) -> None:
        self._uow_factory = uow_factory
        self._guard = guard

    async def execute(
        self, actor: TrustedActor, calendar_id: str, expected_version: int, day: date
    ) -> Calendar:
        async with self._uow_factory.create() as uow:
            original = await self._guard.load(actor, calendar_id, expected_version, uow.calendars)
            revised = remove_date_exception(original, day)
            await uow.calendars.update_if_version(revised, expected_version)
            await uow.commit()
        return revised
