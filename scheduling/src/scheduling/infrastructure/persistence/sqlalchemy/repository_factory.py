"""Infrastructure-only repository construction boundary."""

from sqlalchemy.ext.asyncio import AsyncSession

from .calendar_mapper import CalendarPersistenceMapper
from .calendar_repository import SqlAlchemyCalendarRepository


class SqlAlchemyCalendarRepositoryFactory:
    def __init__(self, mapper: CalendarPersistenceMapper) -> None:
        self._mapper = mapper

    def create(self, session: AsyncSession) -> SqlAlchemyCalendarRepository:
        return SqlAlchemyCalendarRepository(session, self._mapper)
