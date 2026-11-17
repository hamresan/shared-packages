"""Host-injected database sessions; per-operation transaction and tenant isolation."""

from contextlib import AbstractAsyncContextManager
from types import TracebackType
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from customer.application.actor import CustomerActor
from customer.application.contracts import CustomerUnitOfWork, CustomerUnitOfWorkFactory
from customer.application.contracts.audit_repository import CustomerAuditEvent
from customer.infrastructure.persistence.sqlalchemy.repositories.address import (
    SqlAlchemyAddressRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.audit import (
    SqlAlchemyAuditRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.contact import (
    SqlAlchemyContactRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.customer import (
    SqlAlchemyCustomerRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.erasure import (
    SqlAlchemyErasureRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.external_identity import (
    SqlAlchemyExternalIdentityRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.idempotency import (
    SqlAlchemyIdempotencyRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.internal_identity import (
    SqlAlchemyInternalIdentityRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.note import (
    SqlAlchemyNoteRepository,
)
from customer.infrastructure.persistence.sqlalchemy.repositories.preference import (
    SqlAlchemyPreferenceRepository,
)
from customer.infrastructure.persistence.sqlalchemy.tenant_scope import PostgreSqlTenantScope


class SqlAlchemyCustomerUnitOfWork(
    CustomerUnitOfWork, AbstractAsyncContextManager[CustomerUnitOfWork]
):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        business_id: UUID,
        tenant_scope: PostgreSqlTenantScope,
    ) -> None:
        self.session_factory = session_factory
        self.business_id = business_id
        self.tenant_scope = tenant_scope
        self.session: AsyncSession | None = None
        self.committed = False
        self._customers: SqlAlchemyCustomerRepository
        self._contacts: SqlAlchemyContactRepository
        self._addresses: SqlAlchemyAddressRepository
        self._preferences: SqlAlchemyPreferenceRepository
        self._notes: SqlAlchemyNoteRepository
        self._internal_identities: SqlAlchemyInternalIdentityRepository
        self._external_identities: SqlAlchemyExternalIdentityRepository
        self._idempotency: SqlAlchemyIdempotencyRepository
        self._audit: SqlAlchemyAuditRepository
        self._erasure: SqlAlchemyErasureRepository

    @property
    def audit(self) -> SqlAlchemyAuditRepository:
        return self._audit

    @property
    def erasure(self) -> SqlAlchemyErasureRepository:
        return self._erasure

    @property
    def customers(self) -> SqlAlchemyCustomerRepository:
        return self._customers

    @property
    def contacts(self) -> SqlAlchemyContactRepository:
        return self._contacts

    @property
    def addresses(self) -> SqlAlchemyAddressRepository:
        return self._addresses

    @property
    def preferences(self) -> SqlAlchemyPreferenceRepository:
        return self._preferences

    @property
    def notes(self) -> SqlAlchemyNoteRepository:
        return self._notes

    @property
    def internal_identities(self) -> SqlAlchemyInternalIdentityRepository:
        return self._internal_identities

    @property
    def external_identities(self) -> SqlAlchemyExternalIdentityRepository:
        return self._external_identities

    @property
    def idempotency(self) -> SqlAlchemyIdempotencyRepository:
        return self._idempotency

    async def __aenter__(self) -> CustomerUnitOfWork:
        session = self.session_factory()
        self.session = session
        await session.begin()
        try:
            await self.tenant_scope.apply(session, self.business_id)
        except BaseException:
            await session.rollback()
            await session.close()
            raise
        self._customers = SqlAlchemyCustomerRepository(session)
        self._contacts = SqlAlchemyContactRepository(session)
        self._addresses = SqlAlchemyAddressRepository(session)
        self._preferences = SqlAlchemyPreferenceRepository(session)
        self._notes = SqlAlchemyNoteRepository(session)
        self._internal_identities = SqlAlchemyInternalIdentityRepository(session)
        self._external_identities = SqlAlchemyExternalIdentityRepository(session)
        self._idempotency = SqlAlchemyIdempotencyRepository(session)
        self._audit = SqlAlchemyAuditRepository(session)
        self._erasure = SqlAlchemyErasureRepository(session)
        return self

    async def commit_audited(self, actor: CustomerActor, action: str, customer_id: UUID) -> None:
        if actor.business_id != self.business_id:
            raise ValueError("Audit actor business differs from transaction scope")
        await self.audit.add(
            CustomerAuditEvent(
                business_id=self.business_id,
                customer_id=customer_id,
                actor_id=actor.actor_id,
                actor_type=actor.actor_type,
                action=action,
            )
        )
        await self.commit()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work has not entered a transaction")
        await self.session.commit()
        self.committed = True

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self.session is not None:
            try:
                if not self.committed:
                    await self.session.rollback()
            finally:
                await self.session.close()


class SqlAlchemyCustomerUnitOfWorkFactory(CustomerUnitOfWorkFactory):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.tenant_scope = PostgreSqlTenantScope()

    def __call__(self, business_id: UUID) -> AbstractAsyncContextManager[CustomerUnitOfWork]:
        return SqlAlchemyCustomerUnitOfWork(self.session_factory, business_id, self.tenant_scope)
