from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class IdentityTestDatabase(Protocol):
    async def start(self) -> None: ...

    async def close(self) -> None: ...

    def session_factory(self) -> AbstractAsyncContextManager[AsyncSession]: ...
