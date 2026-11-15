"""Fresh Unit of Work per request, sharing only the authorized backing store."""

from .calendar_store import InMemoryCalendarStore
from .unit_of_work import InMemoryCalendarUnitOfWork


class InMemoryCalendarUnitOfWorkFactory:
    def __init__(self, store: InMemoryCalendarStore) -> None:
        self._store = store

    def create(self) -> InMemoryCalendarUnitOfWork:
        return InMemoryCalendarUnitOfWork(self._store)
