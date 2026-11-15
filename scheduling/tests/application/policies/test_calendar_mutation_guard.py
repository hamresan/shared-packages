import pytest

from scheduling.application.errors import CalendarNotFoundError, CalendarVersionConflictError
from scheduling.application.policies import CalendarMutationGuard
from scheduling.domain.calendar import CalendarScope
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_guard_loads_calendar_only_with_management_permission_and_matching_version() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(calendar)
    scenario.grant_calendar(calendar)
    guard = CalendarMutationGuard(scenario.authorizer)
    async with scenario.uow_factory.create() as uow:
        assert await guard.load(scenario.actor, calendar.calendar_id, 1, uow.calendars) == calendar


async def test_guard_rejects_missing_calendar_and_stale_version() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(calendar)
    scenario.grant_calendar(calendar)
    guard = CalendarMutationGuard(scenario.authorizer)
    async with scenario.uow_factory.create() as uow:
        with pytest.raises(CalendarNotFoundError):
            await guard.load(scenario.actor, "unknown", 1, uow.calendars)
        with pytest.raises(CalendarVersionConflictError):
            await guard.load(scenario.actor, calendar.calendar_id, 2, uow.calendars)


async def test_guard_checks_permission_before_disclosing_version() -> None:
    scenario = build_calendar_scenario()
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(calendar)
    guard = CalendarMutationGuard(scenario.authorizer)
    async with scenario.uow_factory.create() as uow:
        with pytest.raises(PermissionError):
            await guard.load(scenario.actor, calendar.calendar_id, 999, uow.calendars)
