"""Host-owned Alembic integration; this package never runs revisions."""

from sqlalchemy import MetaData

from .base import SchedulingBase
from .calendar_record import CalendarRecord


def scheduling_metadata() -> MetaData:
    """Merge this metadata into the host's Alembic target_metadata collection."""
    _ = CalendarRecord.__table__
    return SchedulingBase.metadata


def is_scheduling_table(name: str | None, kind: str) -> bool:
    """Use as one predicate in the host's Alembic include_name filter."""
    return kind == "table" and name is not None and name.startswith("scheduling_")
