"""Transaction fake with explicit commit and rollback-on-exit semantics."""

from types import TracebackType
from typing import Self

from .calendar_repository import InMemoryCalendarRepository
from .calendar_store import InMemoryCalendarStore


class InMemoryCalendarUnitOfWork:
    def __init__(self, store: InMemoryCalendarStore) -> None:
        self.calendars = InMemoryCalendarRepository(store)
        self._store = store
        self._committed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self._committed:
            self.calendars.creates.clear()
            self.calendars.updates.clear()

    async def commit(self) -> None:
        if self._committed:
            raise RuntimeError("Unit of Work cannot be committed more than once.")
        await self._store.commit(tuple(self.calendars.creates), tuple(self.calendars.updates))
        self._committed = True
