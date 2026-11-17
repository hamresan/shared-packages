from contextlib import AbstractAsyncContextManager
from types import TracebackType

from customer.application.contracts import (
    CustomerIdempotencyRepository,
    CustomerRepository,
    CustomerUnitOfWork,
    CustomerUnitOfWorkFactory,
)
from tests.support.fakes.customer_repository import InMemoryCustomerRepository
from tests.support.fakes.idempotency_repository import InMemoryCustomerIdempotencyRepository


class FakeCustomerUnitOfWork(CustomerUnitOfWork):
    def __init__(
        self, customers: CustomerRepository, idempotency: CustomerIdempotencyRepository
    ) -> None:
        self._customers = customers
        self._idempotency = idempotency

    @property
    def customers(self) -> CustomerRepository:
        return self._customers

    @property
    def idempotency(self) -> CustomerIdempotencyRepository:
        return self._idempotency

    async def commit(self) -> None:
        return None


class FakeCustomerUnitOfWorkContext(AbstractAsyncContextManager[CustomerUnitOfWork]):
    def __init__(self, uow: CustomerUnitOfWork) -> None:
        self._uow = uow

    async def __aenter__(self) -> CustomerUnitOfWork:
        return self._uow

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


class FakeCustomerUnitOfWorkFactory(CustomerUnitOfWorkFactory):
    def __init__(self) -> None:
        self.customers = InMemoryCustomerRepository()
        self.idempotency = InMemoryCustomerIdempotencyRepository()

    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]:
        return FakeCustomerUnitOfWorkContext(
            FakeCustomerUnitOfWork(self.customers, self.idempotency)
        )
