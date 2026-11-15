"""Session ownership and transactional guarantees for a single use case."""

from types import TracebackType
from typing import Self

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from scheduling.application.contracts import CalendarRepository
from scheduling.application.errors import CalendarAlreadyExistsError

from .repository_factory import SqlAlchemyCalendarRepositoryFactory


class SqlAlchemyCalendarUnitOfWork:
    """Commit explicitly; rollback and close on every exit path."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repository_factory: SqlAlchemyCalendarRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory
        self._session: AsyncSession | None = None
        self._calendars: CalendarRepository | None = None
        self._committed = False

    @property
    def calendars(self) -> CalendarRepository:
        if self._calendars is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._calendars

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("Unit of Work cannot be entered twice.")
        self._session = self._session_factory()
        self._calendars = self._repository_factory.create(self._session)
        return self

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of Work has not been entered.")
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if self._is_calendar_identity_conflict(exc):
                raise CalendarAlreadyExistsError(
                    "Calendar ID or tenant scope already exists."
                ) from exc
            raise
        self._committed = True

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is not None:
            try:
                if not self._committed or exc_type is not None:
                    await self._session.rollback()
            finally:
                await self._session.close()
                self._session = None
                self._calendars = None

    @staticmethod
    def _is_calendar_identity_conflict(error: IntegrityError) -> bool:
        original = error.orig
        constraint = getattr(original, "constraint_name", None)
        if getattr(original, "sqlstate", None) == "23505":
            return constraint in {
                "uq_scheduling_tenant_scope",
                "scheduling_calendars_pkey",
            } or any(
                name in str(original)
                for name in ("uq_scheduling_tenant_scope", "scheduling_calendars_pkey")
            )
        return "UNIQUE constraint failed: scheduling_calendars." in str(original)
