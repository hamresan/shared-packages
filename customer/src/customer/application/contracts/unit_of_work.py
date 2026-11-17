"""Transaction contract; concrete repositories are added alongside use cases."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol

from customer.application.contracts.customer_repository import CustomerRepository
from customer.application.contracts.idempotency_repository import CustomerIdempotencyRepository


class CustomerUnitOfWork(Protocol):
    @property
    def customers(self) -> CustomerRepository: ...

    @property
    def idempotency(self) -> CustomerIdempotencyRepository: ...

    async def commit(self) -> None: ...


class CustomerUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]: ...
