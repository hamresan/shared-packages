from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSessionFactory(Protocol):
    """Create host-owned async SQLAlchemy session context managers."""

    def __call__(self) -> AbstractAsyncContextManager[AsyncSession]: ...
