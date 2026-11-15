"""Remove a known unavailable interval from the managed calendar."""

from scheduling.domain.calendar import BlockedPeriod, Calendar
from scheduling.domain.calendar.revisions import remove_blocked_period

from ..contracts import CalendarUnitOfWorkFactory
from ..models import TrustedActor
from ..policies import CalendarMutationGuard


class RemoveBlockedPeriod:
    def __init__(
        self, uow_factory: CalendarUnitOfWorkFactory, guard: CalendarMutationGuard
    ) -> None:
        self._uow_factory = uow_factory
        self._guard = guard

    async def execute(
        self, actor: TrustedActor, calendar_id: str, expected_version: int, blocked: BlockedPeriod
    ) -> Calendar:
        async with self._uow_factory.create() as uow:
            original = await self._guard.load(actor, calendar_id, expected_version, uow.calendars)
            revised = remove_blocked_period(original, blocked)
            await uow.calendars.update_if_version(revised, expected_version)
            await uow.commit()
        return revised
