from datetime import time

import pytest

from scheduling.application.errors import CalendarVersionConflictError
from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import UpdateWeeklySchedule
from scheduling.domain.calendar import CalendarScope, DaySchedule, WeeklySchedule, WorkingWindow
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_update_weekly_schedule_preserves_identity_and_increments_version() -> None:
    scenario = build_calendar_scenario()
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(original)
    scenario.grant_calendar(original)
    schedule = WeeklySchedule((DaySchedule(0, (WorkingWindow(time(10), time(13)),)),))
    use_case = UpdateWeeklySchedule(
        scenario.uow_factory, CalendarMutationGuard(scenario.authorizer)
    )

    updated = await use_case.execute(scenario.actor, original.calendar_id, 1, schedule)

    assert updated.weekly_schedule == schedule
    assert updated.version == 2
    assert updated.calendar_id == original.calendar_id
    assert scenario.store.records[(original.tenant_id, original.calendar_id)] == updated


async def test_update_weekly_schedule_rejects_stale_expected_version() -> None:
    scenario = build_calendar_scenario()
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(original)
    scenario.grant_calendar(original)
    use_case = UpdateWeeklySchedule(
        scenario.uow_factory, CalendarMutationGuard(scenario.authorizer)
    )

    await use_case.execute(scenario.actor, original.calendar_id, 1, original.weekly_schedule)
    with pytest.raises(CalendarVersionConflictError):
        await use_case.execute(scenario.actor, original.calendar_id, 1, original.weekly_schedule)

    assert scenario.store.records[(original.tenant_id, original.calendar_id)].version == 2
