"""Transactional boundary owned by a consuming host's infrastructure."""

from types import TracebackType
from typing import Protocol, Self

from .calendar_repository import CalendarRepository


class CalendarUnitOfWork(Protocol):
    @property
    def calendars(self) -> CalendarRepository: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...


class CalendarUnitOfWorkFactory(Protocol):
    def create(self) -> CalendarUnitOfWork: ...
