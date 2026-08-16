from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSessionFactory(Protocol):
    """Creates host-owned SQLAlchemy async-session context managers."""

    def __call__(self) -> AbstractAsyncContextManager[AsyncSession]: ...
