from datetime import UTC, datetime

from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import AddBlockedPeriod, RemoveBlockedPeriod
from scheduling.domain.calendar import BlockedPeriod, CalendarScope
from scheduling.domain.time import UtcInterval
from tests.support.application import build_calendar_scenario
from tests.support.calendar_factory import make_calendar


async def test_blocked_period_can_be_added_and_removed_transactionally() -> None:
    scenario = build_calendar_scenario()
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    scenario.store.seed(original)
    scenario.grant_calendar(original)
    guard = CalendarMutationGuard(scenario.authorizer)
    blocked = BlockedPeriod(
        UtcInterval(datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)),
        reason="Maintenance",
    )

    updated = await AddBlockedPeriod(scenario.uow_factory, guard).execute(
        scenario.actor, original.calendar_id, 1, blocked
    )
    restored = await RemoveBlockedPeriod(scenario.uow_factory, guard).execute(
        scenario.actor, original.calendar_id, 2, blocked
    )

    assert updated.blocked_periods == (blocked,)
    assert restored.blocked_periods == ()
    assert restored.version == 3
