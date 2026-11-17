"""Transaction contract; concrete repositories are added alongside use cases."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.contracts.address_repository import CustomerAddressRepository
from customer.application.contracts.audit_repository import CustomerAuditRepository
from customer.application.contracts.contact_repository import CustomerContactRepository
from customer.application.contracts.customer_repository import CustomerRepository
from customer.application.contracts.erasure_repository import CustomerErasureRepository
from customer.application.contracts.external_identity_repository import (
    CustomerExternalIdentityRepository,
)
from customer.application.contracts.idempotency_repository import CustomerIdempotencyRepository
from customer.application.contracts.internal_identity_repository import (
    CustomerIdentityLinkRepository,
)
from customer.application.contracts.note_repository import CustomerNoteRepository
from customer.application.contracts.preference_repository import CustomerPreferenceRepository


class CustomerUnitOfWork(Protocol):
    @property
    def audit(self) -> CustomerAuditRepository: ...

    @property
    def erasure(self) -> CustomerErasureRepository: ...

    @property
    def internal_identities(self) -> CustomerIdentityLinkRepository: ...

    @property
    def external_identities(self) -> CustomerExternalIdentityRepository: ...

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

    async def commit_audited(
        self, actor: CustomerActor, action: str, customer_id: UUID
    ) -> None: ...


class CustomerUnitOfWorkFactory(Protocol):
    def __call__(self, business_id: UUID) -> AbstractAsyncContextManager[CustomerUnitOfWork]: ...
