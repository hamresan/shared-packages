from collections.abc import AsyncIterator
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSessionFactory(Protocol):
    """Creates SQLAlchemy async sessions owned/configured by the host application."""

    def __call__(self) -> AsyncIterator[AsyncSession]: ...
