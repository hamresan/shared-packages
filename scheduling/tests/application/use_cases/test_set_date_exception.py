from datetime import date

from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import RemoveDateException, SetDateException
from scheduling.domain.calendar import CalendarException, CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_set_and_remove_date_exception_commit_distinct_revisions() -> None:
    scenario = build_calendar_scenario()
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(original)
    scenario.grant_calendar(original)
    guard = CalendarMutationGuard(scenario.authorizer)
    exception = CalendarException(date(2026, 11, 16), closed=True)

    closed = await SetDateException(scenario.uow_factory, guard).execute(
        scenario.actor, original.calendar_id, 1, exception
    )
    restored = await RemoveDateException(scenario.uow_factory, guard).execute(
        scenario.actor, original.calendar_id, 2, exception.day
    )

    assert closed.exceptions == (exception,)
    assert closed.version == 2
    assert restored.exceptions == ()
    assert restored.version == 3
    assert scenario.store.records[(original.tenant_id, original.calendar_id)] == restored
