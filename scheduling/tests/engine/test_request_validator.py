from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from scheduling.domain.calendar import CalendarScope
from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval
from tests.support.calendar_factory import make_calendar, make_request


def test_request_requires_correct_hierarchical_calendar_scopes() -> None:
    with pytest.raises(ValueError, match="Organization calendar"):
        make_request(organization=make_calendar(CalendarScope.LOCATION, "bad-org"))
    with pytest.raises(ValueError, match="Location calendar"):
        make_request(location=make_calendar(CalendarScope.RESOURCE, "bad-location"))
    with pytest.raises(ValueError, match="resource calendar"):
        make_request(resources=(make_calendar(CalendarScope.LOCATION, "bad-resource"),))


def test_request_rejects_cross_tenant_resources() -> None:
    other = make_calendar(CalendarScope.RESOURCE, "resource-b", tenant_id="tenant-b")

    with pytest.raises(ValueError, match="one trusted tenant"):
        make_request(resources=(other,))


def test_request_rejects_duplicate_or_excessive_resource_entries() -> None:
    duplicate = make_calendar(CalendarScope.RESOURCE, "resource-a")
    with pytest.raises(ValueError, match="unique"):
        make_request(resources=(duplicate, duplicate))

    resources = tuple(make_calendar(CalendarScope.RESOURCE, str(index)) for index in range(101))
    with pytest.raises(ValueError, match="100 resources"):
        make_request(resources=resources)


def test_request_rejects_searches_larger_than_31_days() -> None:
    oversized_window = UtcInterval(
        datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 12, 3, tzinfo=UTC)
    )
    with pytest.raises(ValueError, match="31 days"):
        make_request(query_window=oversized_window)


def test_request_requires_an_aware_utc_reference_clock() -> None:
    with pytest.raises(ValueError, match="aware UTC"):
        make_request(now=datetime(2026, 11, 15))
    with pytest.raises(ValueError, match="aware UTC"):
        make_request(now=datetime(2026, 11, 15, tzinfo=timezone(timedelta(hours=4))))


def test_request_rejects_zero_or_subminute_duration_and_step() -> None:
    with pytest.raises(ValueError, match="at least one minute"):
        make_request(duration=timedelta())
    with pytest.raises(ValueError, match="at least one minute"):
        make_request(step=timedelta(seconds=30))


def test_request_rejects_negative_buffers_and_notice() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        make_request(buffer_before=-timedelta(seconds=1))
    with pytest.raises(ValueError, match="cannot be negative"):
        make_request(buffer_after=-timedelta(seconds=1))
    with pytest.raises(ValueError, match="cannot be negative"):
        make_request(minimum_notice=-timedelta(seconds=1))


def test_request_rejects_nonpositive_maximum_horizon() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        make_request(maximum_horizon=timedelta())


def test_request_rejects_busy_periods_for_ineligible_resources() -> None:
    interval = UtcInterval(
        datetime(2026, 11, 16, 5, tzinfo=UTC), datetime(2026, 11, 16, 6, tzinfo=UTC)
    )
    with pytest.raises(ValueError, match="eligible resources"):
        make_request(busy_intervals=(BusyInterval("unknown", interval),))

    with pytest.raises(ValueError, match="cannot be empty"):
        BusyInterval("", interval)


def test_no_resources_is_a_valid_empty_pool() -> None:
    assert replace(make_request(), resources=()).resources == ()
