from datetime import UTC, datetime, timedelta

from subscription import UsagePeriod
from subscription.infrastructure.persistence.sqlalchemy.repositories import (
    CalendarUsageWindowCalculator,
)


def test_week_window_starts_on_monday() -> None:
    at = datetime(2026, 8, 21, 15, 30, tzinfo=UTC)

    window = CalendarUsageWindowCalculator().calculate(UsagePeriod.WEEK, at)

    assert window is not None
    assert window.start == datetime(2026, 8, 17, tzinfo=UTC)
    assert window.end == at


def test_lifetime_window_has_no_start() -> None:
    at = datetime(2026, 8, 21, tzinfo=UTC)

    window = CalendarUsageWindowCalculator().calculate(UsagePeriod.LIFETIME, at)

    assert window is not None
    assert window.start is None


def test_non_calendar_period_is_deferred_to_subscription_resolver() -> None:
    at = datetime(2026, 8, 21, tzinfo=UTC)

    assert CalendarUsageWindowCalculator().calculate(UsagePeriod.TRIAL, at) is None
