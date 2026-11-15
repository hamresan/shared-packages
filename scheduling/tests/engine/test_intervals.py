from datetime import UTC, datetime, timedelta

from scheduling.domain.time import UtcInterval
from scheduling.engine.intervals import (
    intersect_intervals,
    merge_intervals,
    subtract_intervals,
)


def interval(start_hour: int, end_hour: int) -> UtcInterval:
    day = datetime(2026, 11, 16, tzinfo=UTC)
    return UtcInterval(day + timedelta(hours=start_hour), day + timedelta(hours=end_hour))


def test_merge_joins_adjacent_and_overlapping_intervals() -> None:
    assert merge_intervals((interval(9, 11), interval(10, 12), interval(12, 13))) == (
        interval(9, 13),
    )


def test_merge_empty_is_empty() -> None:
    assert merge_intervals(()) == ()


def test_intersection_excludes_touching_boundaries() -> None:
    assert intersect_intervals((interval(9, 12),), (interval(11, 13),)) == (interval(11, 12),)
    assert intersect_intervals((interval(9, 12),), (interval(12, 15),)) == ()


def test_intersection_walks_independently_sized_sets() -> None:
    assert intersect_intervals((interval(9, 10), interval(12, 15)), (interval(8, 13),)) == (
        interval(9, 10),
        interval(12, 13),
    )


def test_subtraction_splits_working_hours_without_zero_length_ranges() -> None:
    assert subtract_intervals((interval(9, 17),), (interval(10, 11), interval(12, 14))) == (
        interval(9, 10),
        interval(11, 12),
        interval(14, 17),
    )


def test_subtraction_handles_complete_and_external_blocks() -> None:
    assert subtract_intervals((interval(9, 17),), (interval(8, 18),)) == ()
    assert subtract_intervals((interval(9, 17),), (interval(7, 8),)) == (interval(9, 17),)
