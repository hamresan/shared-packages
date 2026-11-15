from datetime import date, time

import pytest

from scheduling.domain.calendar import DaySchedule, WeeklySchedule, WorkingWindow


def test_weekly_schedule_supports_split_shifts_and_closed_days() -> None:
    schedule = WeeklySchedule(
        days=(
            DaySchedule(
                weekday=0,
                windows=(WorkingWindow(time(9), time(12)), WorkingWindow(time(13), time(17))),
            ),
        )
    )

    assert len(schedule.windows_for(date(2026, 11, 16))) == 2
    assert schedule.windows_for(date(2026, 11, 17)) == ()


def test_weekly_schedule_rejects_overlapping_windows() -> None:
    with pytest.raises(ValueError, match="overlap"):
        DaySchedule(0, (WorkingWindow(time(9), time(12)), WorkingWindow(time(11), time(15))))


def test_weekly_schedule_rejects_overlaps_across_days() -> None:
    with pytest.raises(ValueError, match="overlap"):
        WeeklySchedule(
            (
                DaySchedule(0, (WorkingWindow(time(22), time(2)),)),
                DaySchedule(1, (WorkingWindow(time(1), time(5)),)),
            )
        )


def test_weekly_schedule_rejects_overlaps_across_sunday_and_monday() -> None:
    with pytest.raises(ValueError, match="week boundary"):
        WeeklySchedule(
            (
                DaySchedule(6, (WorkingWindow(time(22), time(2)),)),
                DaySchedule(0, (WorkingWindow(time(1), time(5)),)),
            )
        )


def test_weekly_schedule_allows_adjacent_windows() -> None:
    schedule = WeeklySchedule(
        (DaySchedule(0, (WorkingWindow(time(9), time(12)), WorkingWindow(time(12), time(17)))),)
    )

    assert len(schedule.windows_for(date(2026, 11, 16))) == 2


def test_weekly_schedule_rejects_duplicate_weekday_entries() -> None:
    with pytest.raises(ValueError, match="only once"):
        WeeklySchedule((DaySchedule(0, ()), DaySchedule(0, ())))


@pytest.mark.parametrize("weekday", [-1, 7, True])
def test_day_schedule_rejects_invalid_weekday(weekday: int) -> None:
    with pytest.raises(ValueError):
        DaySchedule(weekday, ())
