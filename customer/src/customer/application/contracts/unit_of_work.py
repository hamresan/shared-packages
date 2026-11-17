"""Transaction contract; concrete repositories are added alongside use cases."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol

from customer.application.contracts.address_repository import CustomerAddressRepository
from customer.application.contracts.contact_repository import CustomerContactRepository
from customer.application.contracts.customer_repository import CustomerRepository
from customer.application.contracts.idempotency_repository import CustomerIdempotencyRepository
from customer.application.contracts.note_repository import CustomerNoteRepository
from customer.application.contracts.preference_repository import CustomerPreferenceRepository


class CustomerUnitOfWork(Protocol):
    @property
    def addresses(self) -> CustomerAddressRepository: ...

    @property
    def preferences(self) -> CustomerPreferenceRepository: ...

    @property
    def notes(self) -> CustomerNoteRepository: ...

    @property
    def contacts(self) -> CustomerContactRepository: ...

    @property
    def customers(self) -> CustomerRepository: ...

    @property
    def idempotency(self) -> CustomerIdempotencyRepository: ...

    async def commit(self) -> None: ...


class CustomerUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]: ...
