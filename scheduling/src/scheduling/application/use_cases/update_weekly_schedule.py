"""Replace recurring hours without overwriting another editor's changes."""

from scheduling.domain.calendar import Calendar, WeeklySchedule
from scheduling.domain.calendar.revisions import update_weekly_schedule

from ..contracts import CalendarUnitOfWorkFactory
from ..models import TrustedActor
from ..policies import CalendarMutationGuard


class UpdateWeeklySchedule:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, guard: CalendarMutationGuard
    ) -> None:
        self._uow_factory = uow_factory
        self._guard = guard

    async def execute(
        self, actor: TrustedActor, calendar_id: str, expected_version: int, schedule: WeeklySchedule
    ) -> Calendar:
        async with self._uow_factory.create() as uow:
            original = await self._guard.load(actor, calendar_id, expected_version, uow.calendars)
            revised = update_weekly_schedule(original, schedule)
            await uow.calendars.update_if_version(revised, expected_version)
            await uow.commit()
        return revised
