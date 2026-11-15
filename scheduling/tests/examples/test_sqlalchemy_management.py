"""Acceptance coverage for the documented SQLAlchemy host example."""

from datetime import time

from examples.sqlalchemy_management import run_demo


async def test_sqlalchemy_management_example_round_trips_revision() -> None:
    calendar = await run_demo()

    assert calendar.version == 2
    assert calendar.weekly_schedule.days[0].windows[0].start == time(10)
    assert calendar.weekly_schedule.days[0].windows[0].end == time(14)
