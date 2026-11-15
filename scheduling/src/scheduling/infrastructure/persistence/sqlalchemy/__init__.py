"""Optional SQLAlchemy 2 adapter; no SQLAlchemy import in the package core."""

from .calendar_mapper import CalendarPersistenceMapper
from .calendar_record import CalendarRecord
from .calendar_repository import SqlAlchemyCalendarRepository
from .migration_type_renderer import render_scheduling_type
from .migrations import is_scheduling_table, scheduling_metadata
from .repository_factory import SqlAlchemyCalendarRepositoryFactory
from .unit_of_work import SqlAlchemyCalendarUnitOfWork
from .unit_of_work_factory import SqlAlchemyCalendarUnitOfWorkFactory

__all__ = [
    "CalendarPersistenceMapper",
    "CalendarRecord",
    "SqlAlchemyCalendarRepository",
    "SqlAlchemyCalendarRepositoryFactory",
    "SqlAlchemyCalendarUnitOfWork",
    "SqlAlchemyCalendarUnitOfWorkFactory",
    "is_scheduling_table",
    "render_scheduling_type",
    "scheduling_metadata",
]
