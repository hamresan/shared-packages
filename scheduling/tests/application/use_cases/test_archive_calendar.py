import pytest

from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import ArchiveCalendar, UpdateWeeklySchedule
from scheduling.domain.calendar import CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_archive_preserves_calendar_and_disables_future_mutations() -> None:
    scenario = build_calendar_scenario()
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(original)
    scenario.grant_calendar(original)
    guard = CalendarMutationGuard(scenario.authorizer)

    archived = await ArchiveCalendar(scenario.uow_factory, guard).execute(
        scenario.actor, original.calendar_id, 1
    )

    assert archived.archived
    assert archived.version == 2
    assert archived.calendar_id == original.calendar_id
    with pytest.raises(ValueError, match="Archived calendars"):
        await UpdateWeeklySchedule(scenario.uow_factory, guard).execute(
            scenario.actor, archived.calendar_id, 2, archived.weekly_schedule
        )
    assert scenario.store.records[(archived.tenant_id, archived.calendar_id)] == archived


async def test_actor_authorized_for_one_resource_cannot_archive_another() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-b")
    scenario.store.seed(calendar)
    scenario.grant_scope(CalendarScope.RESOURCE, "resource-a")

    with pytest.raises(PermissionError):
        await ArchiveCalendar(
            scenario.uow_factory, CalendarMutationGuard(scenario.authorizer)
        ).execute(scenario.actor, calendar.calendar_id, 1)

    assert not scenario.store.records[(calendar.tenant_id, calendar.calendar_id)].archived
