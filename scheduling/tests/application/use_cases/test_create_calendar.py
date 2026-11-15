from dataclasses import replace

import pytest

from scheduling.application.errors import CalendarAlreadyExistsError, CrossTenantCalendarError
from scheduling.application.use_cases import CreateCalendar
from scheduling.domain.calendar import CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_create_calendar_commits_authorized_tenant_scoped_record() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.grant_calendar(calendar)

    result = await CreateCalendar(scenario.uow_factory, scenario.authorizer).execute(
        scenario.actor, calendar
    )

    assert result == calendar
    assert scenario.store.records[("tenant-a", calendar.calendar_id)] == calendar


async def test_create_calendar_denies_foreign_tenant_even_when_scope_is_granted() -> None:
    scenario = build_calendar_scenario()
    foreign = make_calendar(CalendarScope.RESOURCE, "resource-a", tenant_id="tenant-b")
    scenario.grant_calendar(foreign)

    with pytest.raises(CrossTenantCalendarError):
        await CreateCalendar(scenario.uow_factory, scenario.authorizer).execute(
            scenario.actor, foreign
        )

    assert scenario.store.records == {}


async def test_create_calendar_denies_unauthorized_scope() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")

    with pytest.raises(PermissionError):
        await CreateCalendar(scenario.uow_factory, scenario.authorizer).execute(
            scenario.actor, calendar
        )

    assert scenario.store.records == {}


async def test_duplicate_calendar_id_and_scope_cannot_be_committed() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.grant_calendar(calendar)
    use_case = CreateCalendar(scenario.uow_factory, scenario.authorizer)
    await use_case.execute(scenario.actor, calendar)

    with pytest.raises(CalendarAlreadyExistsError):
        await use_case.execute(scenario.actor, calendar)
    with pytest.raises(CalendarAlreadyExistsError):
        await use_case.execute(scenario.actor, replace(calendar, calendar_id="another-id"))

    assert len(scenario.store.records) == 1


async def test_create_calendar_rejects_archived_or_revised_snapshots() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.grant_calendar(calendar)
    use_case = CreateCalendar(scenario.uow_factory, scenario.authorizer)

    with pytest.raises(ValueError, match="version one"):
        await use_case.execute(scenario.actor, replace(calendar, version=4))
    with pytest.raises(ValueError, match="active"):
        await use_case.execute(scenario.actor, replace(calendar, archived=True))

    assert scenario.store.records == {}
