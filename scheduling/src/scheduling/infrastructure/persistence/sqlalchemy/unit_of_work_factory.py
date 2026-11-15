"""Injectable Unit of Work factory for host composition."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repository_factory import SqlAlchemyCalendarRepositoryFactory
from .unit_of_work import SqlAlchemyCalendarUnitOfWork


class SqlAlchemyCalendarUnitOfWorkFactory:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repository_factory: SqlAlchemyCalendarRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory

    def create(self) -> SqlAlchemyCalendarUnitOfWork:
        return SqlAlchemyCalendarUnitOfWork(self._session_factory, self._repository_factory)
