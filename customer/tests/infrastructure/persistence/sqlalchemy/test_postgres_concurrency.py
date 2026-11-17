"""Stage 8 PostgreSQL acceptance for real races, retries and pooled RLS."""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from customer import (
    CreateCustomerCommand,
    CustomerActor,
    CustomerIdempotencyConflictError,
    CustomerModule,
    CustomerModuleConfig,
    CustomerVersionConflictError,
)
from customer.infrastructure.persistence.sqlalchemy.models import (
    CustomerAuditModel,
    CustomerExternalIdentityModel,
)
from customer.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyCustomerUnitOfWorkFactory,
)
from customer.migrations import customer_metadata
from tests.support.factories.customer import new_customer
from tests.support.factories.customer_module import build_actor
from tests.support.fakes.authorization import AllowCustomerAuthorizer
from tests.support.fakes.clock import FixedClock
from tests.support.fakes.external_evidence import FakeExternalEvidenceVerifier
from tests.support.fakes.fingerprinter import FakeCustomerCreationFingerprinter
from tests.support.fakes.identifiers import RandomIdentifierGenerator
from tests.support.fakes.identity_verification import AcceptIdentityVerifier


def create_module(sessions: async_sessionmaker[AsyncSession]) -> CustomerModule:
    return CustomerModule(
        CustomerModuleConfig(
            unit_of_work_factory=SqlAlchemyCustomerUnitOfWorkFactory(sessions),
            authorizer=AllowCustomerAuthorizer(),
            identity_verifier=AcceptIdentityVerifier(),
            clock=FixedClock(),
            identifiers=RandomIdentifierGenerator(),
            creation_fingerprinter=FakeCustomerCreationFingerprinter(),
            external_evidence_verifier=FakeExternalEvidenceVerifier(),
        )
    )


async def test_guest_creation_retry_conflict_scope_and_expiry(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    """Simulated lost response must not create a duplicate within receipt retention."""
    module = create_module(postgres_sessions)
    first = build_actor(uuid4())
    second = build_actor(uuid4())
    key = "transport-request-77"

    async def create(actor_business: UUID, actor: CustomerActor) -> UUID:
        result = await module.customers.create.execute(
            CreateCustomerCommand(actor_business, actor, "Guest", key)
        )
        return result.id

    first_id, retry_id = await asyncio.gather(
        create(first.business_id, first), create(first.business_id, first)
    )
    assert first_id == retry_id

    # The commit already happened, but the caller lost its response.
    with pytest.raises(TimeoutError):
        await module.customers.create.execute(
            CreateCustomerCommand(first.business_id, first, "Guest", key)
        )
        raise TimeoutError("simulated transport disconnect after commit")
    recovered = await module.customers.create.execute(
        CreateCustomerCommand(first.business_id, first, "Guest", key)
    )
    assert recovered.id == first_id

    with pytest.raises(CustomerIdempotencyConflictError):
        await module.customers.create.execute(
            CreateCustomerCommand(first.business_id, first, "Changed", key)
        )
    other = await module.customers.create.execute(
        CreateCustomerCommand(second.business_id, second, "Guest", key)
    )
    assert other.id != first_id

    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    async with factory(first.business_id) as uow:
        assert (
            await uow.idempotency.prune_expired(
                first.business_id, datetime.now(UTC) + timedelta(days=2)
            )
            == 1
        )
        await uow.commit()
    new_after_expiry = await module.customers.create.execute(
        CreateCustomerCommand(first.business_id, first, "Guest", key)
    )
    assert new_after_expiry.id != first_id


async def test_concurrent_profile_cas_has_one_winner_and_one_audit(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    actor = build_actor(uuid4())
    customer = new_customer(actor.business_id)
    async with factory(actor.business_id) as uow:
        await uow.customers.add(customer)
        await uow.commit_audited(actor, "customer.create", customer.id)

    async def compete(name: str) -> str:
        async with factory(actor.business_id) as uow:
            loaded = await uow.customers.get(actor.business_id, customer.id)
            assert loaded is not None
            loaded.update_profile(name, datetime.now(UTC))
            await uow.customers.save(loaded, 1)
            await uow.commit_audited(actor, "customer.update", customer.id)
            return name

    results = await asyncio.gather(compete("One"), compete("Two"), return_exceptions=True)
    assert sum(isinstance(result, CustomerVersionConflictError) for result in results) == 1
    assert sum(isinstance(result, str) for result in results) == 1
    async with factory(actor.business_id) as uow:
        stored = await uow.customers.get(actor.business_id, customer.id)
        assert stored is not None and stored.version == 2
    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :scope, true)"),
            {"scope": str(actor.business_id)},
        )
        actions = (
            await session.scalars(
                select(CustomerAuditModel.action).where(
                    CustomerAuditModel.customer_id == customer.id
                )
            )
        ).all()
        assert actions.count("customer.update") == 1


async def test_racing_external_links_cannot_duplicate_active_namespace(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    business = uuid4()
    first, second = new_customer(business), new_customer(business)
    async with factory(business) as uow:
        await uow.customers.add(first)
        await uow.customers.add(second)
        await uow.commit()

    async def insert(customer_id: UUID) -> UUID:
        async with postgres_sessions() as session, session.begin():
            await session.execute(
                text("SELECT set_config('app.customer_business_id', :scope, true)"),
                {"scope": str(business)},
            )
            now = datetime.now(UTC)
            session.add(
                CustomerExternalIdentityModel(
                    id=uuid4(),
                    business_id=business,
                    customer_id=customer_id,
                    provider="telegram",
                    channel_account_id="bot",
                    external_user_id="same",
                    status="active",
                    linked_at=now,
                    verification_method="provider_assertion",
                    verified_at=now,
                )
            )
        return customer_id

    results = await asyncio.gather(insert(first.id), insert(second.id), return_exceptions=True)
    assert sum(isinstance(result, UUID) for result in results) == 1
    assert sum(isinstance(result, IntegrityError) for result in results) == 1
    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :scope, true)"),
            {"scope": str(business)},
        )
        assert (
            await session.scalar(select(func.count()).select_from(CustomerExternalIdentityModel))
            == 1
        )


async def test_rls_all_owned_tables_and_pool_context_isolation(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    """Every owned table is forced to RLS even when sessions reuse pooled connections."""
    async with postgres_sessions() as session, session.begin():
        rows = (
            await session.execute(
                text(
                    "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
                    "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "WHERE n.nspname=current_schema() AND c.relname LIKE 'customer_%' "
                    "AND c.relkind='r'"
                )
            )
        ).all()
        assert {row[0] for row in rows} == set(customer_metadata().tables)
        assert all(row[1] and row[2] for row in rows)

    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    first_business, second_business = uuid4(), uuid4()
    first = new_customer(first_business)
    async with factory(first_business) as uow:
        await uow.customers.add(first)
        await uow.commit()

    for _ in range(4):
        async with factory(second_business) as uow:
            assert await uow.customers.get(second_business, first.id) is None
        async with postgres_sessions() as session, session.begin():
            assert (
                await session.scalar(
                    text("SELECT NULLIF(current_setting('app.customer_business_id', true), '')")
                )
                is None
            )
            assert (await session.scalars(select(CustomerExternalIdentityModel))).all() == []
