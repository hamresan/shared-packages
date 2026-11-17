from contextlib import AbstractAsyncContextManager
from types import TracebackType

from customer.application.contracts import CustomerUnitOfWork, CustomerUnitOfWorkFactory


class FakeCustomerUnitOfWork(CustomerUnitOfWork):
    async def commit(self) -> None:
        return None


class FakeCustomerUnitOfWorkContext(AbstractAsyncContextManager[CustomerUnitOfWork]):
    async def __aenter__(self) -> CustomerUnitOfWork:
        return FakeCustomerUnitOfWork()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


class FakeCustomerUnitOfWorkFactory(CustomerUnitOfWorkFactory):
    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]:
        return FakeCustomerUnitOfWorkContext()
