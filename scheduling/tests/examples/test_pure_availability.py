"""Acceptance coverage for the documented standalone calculation example."""

from examples.pure_availability import calculate_demo_slots


def test_readme_demo_calculates_real_resource_slots() -> None:
    actual = [
        (slot.resource_id, slot.interval.start.isoformat(), slot.interval.end.isoformat())
        for slot in calculate_demo_slots()
    ]
    assert actual == [
        ("staff-a", "2026-11-16T05:00:00+00:00", "2026-11-16T05:30:00+00:00"),
        ("staff-a", "2026-11-16T06:00:00+00:00", "2026-11-16T06:30:00+00:00"),
        ("staff-a", "2026-11-16T06:30:00+00:00", "2026-11-16T07:00:00+00:00"),
        ("staff-b", "2026-11-16T09:00:00+00:00", "2026-11-16T09:30:00+00:00"),
        ("staff-b", "2026-11-16T09:30:00+00:00", "2026-11-16T10:00:00+00:00"),
        ("staff-b", "2026-11-16T10:00:00+00:00", "2026-11-16T10:30:00+00:00"),
        ("staff-b", "2026-11-16T10:30:00+00:00", "2026-11-16T11:00:00+00:00"),
    ]
