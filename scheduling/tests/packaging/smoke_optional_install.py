"""Verify optional production adapters load from an installed wheel."""

from scheduling.infrastructure.api.fastapi import (
    AvailabilityHttpMapper,
    CalendarHttpMapper,
    create_calendar_router,
)
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    scheduling_metadata,
)

assert callable(create_calendar_router)
assert isinstance(CalendarHttpMapper(), CalendarHttpMapper)
assert isinstance(AvailabilityHttpMapper(), AvailabilityHttpMapper)
assert isinstance(CalendarPersistenceMapper(), CalendarPersistenceMapper)
assert SqlAlchemyCalendarRepositoryFactory.__name__.startswith("SqlAlchemy")
assert "scheduling_calendars" in scheduling_metadata().tables
