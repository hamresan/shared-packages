from datetime import UTC, date, datetime, time

import pytest

from scheduling.domain.time import (
    AmbiguousLocalTimeError,
    IanaTimeZone,
    NonexistentLocalTimeError,
    resolve_local_datetime,
)


def test_muscat_local_time_resolves_to_correct_utc_instant() -> None:
    local = resolve_local_datetime(date(2026, 11, 15), time(9), IanaTimeZone("Asia/Muscat"))

    assert local.astimezone(UTC) == datetime(2026, 11, 15, 5, tzinfo=UTC)


def test_london_summer_time_uses_the_actual_seasonal_offset() -> None:
    local = resolve_local_datetime(date(2026, 7, 15), time(9), IanaTimeZone("Europe/London"))

    assert local.astimezone(UTC) == datetime(2026, 7, 15, 8, tzinfo=UTC)


def test_nonexistent_london_spring_time_is_rejected() -> None:
    with pytest.raises(NonexistentLocalTimeError):
        resolve_local_datetime(date(2026, 3, 29), time(1, 30), IanaTimeZone("Europe/London"))


def test_ambiguous_london_autumn_time_is_rejected_by_default() -> None:
    with pytest.raises(AmbiguousLocalTimeError):
        resolve_local_datetime(date(2026, 10, 25), time(1, 30), IanaTimeZone("Europe/London"))


def test_ambiguous_london_time_can_explicitly_select_either_utc_instant() -> None:
    zone = IanaTimeZone("Europe/London")

    earlier = resolve_local_datetime(date(2026, 10, 25), time(1, 30), zone, ambiguous="earlier")
    later = resolve_local_datetime(date(2026, 10, 25), time(1, 30), zone, ambiguous="later")

    assert earlier.astimezone(UTC) == datetime(2026, 10, 25, 0, 30, tzinfo=UTC)
    assert later.astimezone(UTC) == datetime(2026, 10, 25, 1, 30, tzinfo=UTC)


def test_local_resolution_rejects_aware_clock_times() -> None:
    with pytest.raises(TypeError):
        resolve_local_datetime(date(2026, 11, 15), time(9, tzinfo=UTC), IanaTimeZone("UTC"))


def test_local_resolution_rejects_datetime_as_calendar_date() -> None:
    with pytest.raises(TypeError):
        resolve_local_datetime(
            datetime(2026, 11, 15, 9),  # type: ignore[arg-type]
            time(9),
            IanaTimeZone("UTC"),
        )


def test_local_resolution_rejects_unknown_ambiguity_policy() -> None:
    with pytest.raises(ValueError):
        resolve_local_datetime(
            date(2026, 11, 15),
            time(9),
            IanaTimeZone("UTC"),
            ambiguous="guess",  # type: ignore[arg-type]
        )
