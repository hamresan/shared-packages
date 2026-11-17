from contextlib import AbstractAsyncContextManager
from types import TracebackType

from customer.application.contracts import (
    CustomerIdempotencyRepository,
    CustomerRepository,
    CustomerUnitOfWork,
    CustomerUnitOfWorkFactory,
)
from customer.application.contracts.address_repository import CustomerAddressRepository
from customer.application.contracts.contact_repository import CustomerContactRepository
from customer.application.contracts.external_identity_repository import (
    CustomerExternalIdentityRepository,
)
from customer.application.contracts.internal_identity_repository import (
    CustomerIdentityLinkRepository,
)
from customer.application.contracts.note_repository import CustomerNoteRepository
from customer.application.contracts.preference_repository import CustomerPreferenceRepository
from tests.support.fakes.address_repository import InMemoryAddressRepository
from tests.support.fakes.contact_repository import InMemoryContactRepository
from tests.support.fakes.customer_repository import InMemoryCustomerRepository
from tests.support.fakes.external_identity_repository import InMemoryExternalIdentityRepository
from tests.support.fakes.idempotency_repository import InMemoryCustomerIdempotencyRepository
from tests.support.fakes.internal_identity_repository import InMemoryIdentityLinkRepository
from tests.support.fakes.note_repository import InMemoryNoteRepository
from tests.support.fakes.preference_repository import InMemoryPreferenceRepository


class FakeCustomerUnitOfWork(CustomerUnitOfWork):
    def __init__(
        self,
        customers: CustomerRepository,
        idempotency: CustomerIdempotencyRepository,
        contacts: CustomerContactRepository,
        addresses: CustomerAddressRepository,
        preferences: CustomerPreferenceRepository,
        notes: CustomerNoteRepository,
        internal_identities: CustomerIdentityLinkRepository,
        external_identities: CustomerExternalIdentityRepository,
    ) -> None:
        self._customers = customers
        self._idempotency = idempotency
        self._contacts = contacts
        self._addresses = addresses
        self._preferences = preferences
        self._notes = notes
        self._internal_identities = internal_identities
        self._external_identities = external_identities

    @property
    def internal_identities(self) -> CustomerIdentityLinkRepository:
        return self._internal_identities

    @property
    def external_identities(self) -> CustomerExternalIdentityRepository:
        return self._external_identities

    @property
    def addresses(self) -> CustomerAddressRepository:
        return self._addresses

    @property
    def preferences(self) -> CustomerPreferenceRepository:
        return self._preferences

    @property
    def notes(self) -> CustomerNoteRepository:
        return self._notes

    @property
    def contacts(self) -> CustomerContactRepository:
        return self._contacts

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
        self.contacts = InMemoryContactRepository()
        self.addresses = InMemoryAddressRepository()
        self.preferences = InMemoryPreferenceRepository()
        self.notes = InMemoryNoteRepository()
        self.internal_identities = InMemoryIdentityLinkRepository()
        self.external_identities = InMemoryExternalIdentityRepository()

    def __call__(self) -> AbstractAsyncContextManager[CustomerUnitOfWork]:
        return FakeCustomerUnitOfWorkContext(
            FakeCustomerUnitOfWork(
                self.customers,
                self.idempotency,
                self.contacts,
                self.addresses,
                self.preferences,
                self.notes,
                self.internal_identities,
                self.external_identities,
            )
        )
