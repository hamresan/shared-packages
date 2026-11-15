import pytest

from scheduling.application.errors import CalendarNotFoundError
from scheduling.application.models import TrustedActor
from scheduling.application.use_cases import GetCalendar
from scheduling.domain.calendar import CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_get_calendar_requires_authorized_scope() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(calendar)
    use_case = GetCalendar(scenario.uow_factory, scenario.authorizer)

    with pytest.raises(PermissionError):
        await use_case.execute(scenario.actor, calendar.calendar_id)

    scenario.authorizer.allow_read(scenario.actor, calendar.scope, calendar.scope_id)
    assert await use_case.execute(scenario.actor, calendar.calendar_id) == calendar


async def test_get_calendar_cannot_read_another_tenants_record() -> None:
    scenario = build_calendar_scenario()
    foreign = make_calendar(CalendarScope.RESOURCE, "resource-a", tenant_id="tenant-b")
    scenario.store.seed(foreign)
    scenario.grant_scope(CalendarScope.RESOURCE, "resource-a")

    with pytest.raises(CalendarNotFoundError):
        await GetCalendar(scenario.uow_factory, scenario.authorizer).execute(
            TrustedActor("tenant-a", "actor-a"), foreign.calendar_id
        )
