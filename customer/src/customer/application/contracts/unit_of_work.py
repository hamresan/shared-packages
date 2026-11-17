"""Transaction contract; concrete repositories are added alongside use cases."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol


class CustomerUnitOfWork(Protocol):
    async def commit(self) -> None: ...


class CustomerUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]: ...
