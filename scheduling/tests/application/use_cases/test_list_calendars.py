import pytest

from scheduling.application.use_cases import ListCalendars
from scheduling.domain.calendar import CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_list_calendars_returns_only_authorized_tenant_scope() -> None:
    scenario = build_calendar_scenario()
    expected = make_calendar(CalendarScope.RESOURCE, "resource-a")
    different = make_calendar(CalendarScope.RESOURCE, "resource-b")
    foreign = make_calendar(CalendarScope.RESOURCE, "resource-a", tenant_id="tenant-b")
    scenario.store.seed(expected)
    scenario.store.seed(different)
    scenario.store.seed(foreign)
    scenario.authorizer.allow_read(scenario.actor, CalendarScope.RESOURCE, "resource-a")

    calendars = await ListCalendars(scenario.uow_factory, scenario.authorizer).execute(
        scenario.actor, CalendarScope.RESOURCE, "resource-a"
    )

    assert calendars == (expected,)


async def test_list_calendars_rejects_unapproved_scope_before_reading() -> None:
    scenario = build_calendar_scenario()

    with pytest.raises(PermissionError):
        await ListCalendars(scenario.uow_factory, scenario.authorizer).execute(
            scenario.actor, CalendarScope.LOCATION, "not-allowed"
        )
