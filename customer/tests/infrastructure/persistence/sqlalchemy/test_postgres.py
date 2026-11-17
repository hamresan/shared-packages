"""Database-backed tenant isolation, integrity, optimistic writes and retries."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from customer.application.contracts import CustomerCreationReceipt
from customer.domain.customer import Customer, CustomerStatus
from customer.domain.errors import CustomerVersionConflictError
from customer.infrastructure.persistence.sqlalchemy.models import (
    CustomerContactModel,
    CustomerExternalIdentityModel,
    CustomerModel,
)
from customer.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyCustomerUnitOfWorkFactory,
)


def new_customer(business_id: UUID, customer_id: UUID | None = None) -> Customer:
    now = datetime.now(UTC)
    return Customer(
        id=customer_id or uuid4(),
        business_id=business_id,
        display_name="Example",
        status=CustomerStatus.ACTIVE,
        version=1,
        created_at=now,
        updated_at=now,
    )


async def test_rls_fails_closed_and_rejects_cross_business_writes(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    first, second = uuid4(), uuid4()
    customer = new_customer(first)
    async with factory(first) as uow:
        await uow.customers.add(customer)
        await uow.commit()
    async with factory(second) as uow:
        assert await uow.customers.get(second, customer.id) is None
        assert await uow.customers.search(second, None, 0, 10) == ()
        with pytest.raises(DBAPIError):
            await uow.customers.add(new_customer(first))
            await uow.commit()

    async with postgres_sessions() as session, session.begin():
        assert (
            await session.scalar(
                text("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
            )
            is False
        )
        assert (await session.scalars(select(CustomerModel))).all() == []
        with pytest.raises(DBAPIError):
            await session.execute(
                text(
                    "INSERT INTO customer_customers "
                    "(id,business_id,display_name,status,version,created_at,updated_at) "
                    "VALUES (:id,:bid,'X','active',1,now(),now())"
                ),
                {"id": uuid4(), "bid": first},
            )


async def test_composite_foreign_key_rejects_cross_business_child(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    first, second = uuid4(), uuid4()
    customer = new_customer(first)
    async with factory(first) as uow:
        await uow.customers.add(customer)
        await uow.commit()
    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :business, true)"),
            {"business": str(second)},
        )
        session.add(
            CustomerContactModel(
                id=uuid4(),
                business_id=second,
                customer_id=customer.id,
                kind="email",
                value="someone@example.org",
                is_primary=True,
                created_at=datetime.now(UTC),
            )
        )
        with pytest.raises(IntegrityError):
            await session.flush()


async def test_optimistic_update_and_transaction_rollback(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    business = uuid4()
    customer = new_customer(business)
    async with factory(business) as uow:
        await uow.customers.add(customer)
        await uow.commit()
    async with factory(business) as uow:
        stale = await uow.customers.get(business, customer.id)
        assert stale is not None
        stale.update_profile("Updated", datetime.now(UTC))
        await uow.customers.save(stale, 1)
        await uow.commit()
    async with factory(business) as uow:
        stale.update_profile("Stale", datetime.now(UTC))
        with pytest.raises(CustomerVersionConflictError):
            await uow.customers.save(stale, 1)
    async with factory(business) as uow:
        fresh = await uow.customers.get(business, customer.id)
        assert fresh is not None and fresh.display_name == "Updated" and fresh.version == 2


async def test_concurrent_idempotency_replays_single_customer(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    business = uuid4()

    async def create_or_replay() -> UUID:
        async with factory(business) as uow:
            await uow.idempotency.lock_key(business, "operation-123")
            existing = await uow.idempotency.find(business, "operation-123")
            if existing is not None:
                return existing.customer_id
            customer = new_customer(business)
            await uow.customers.add(customer)
            await uow.idempotency.add(
                CustomerCreationReceipt(business, "operation-123", "fixed-fingerprint", customer.id)
            )
            await uow.commit()
            return customer.id

    first, second = await asyncio.gather(create_or_replay(), create_or_replay())
    assert first == second
    async with factory(business) as uow:
        customers = await uow.customers.search(business, None, 0, 10)
        assert len(customers) == 1


async def test_partial_unique_indexes_reject_active_duplicates(
    postgres_sessions: async_sessionmaker[AsyncSession],
) -> None:
    factory = SqlAlchemyCustomerUnitOfWorkFactory(postgres_sessions)
    business = uuid4()
    customer = new_customer(business)
    async with factory(business) as uow:
        await uow.customers.add(customer)
        await uow.commit()

    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :business, true)"),
            {"business": str(business)},
        )
        now = datetime.now(UTC)
        session.add_all(
            [
                CustomerContactModel(
                    id=uuid4(),
                    business_id=business,
                    customer_id=customer.id,
                    kind="email",
                    value="a@example.org",
                    is_primary=True,
                    created_at=now,
                ),
                CustomerExternalIdentityModel(
                    id=uuid4(),
                    business_id=business,
                    customer_id=customer.id,
                    provider="telegram",
                    channel_account_id="channel",
                    external_user_id="user",
                    status="active",
                    linked_at=now,
                    verification_method="provider_assertion",
                    verified_at=now,
                ),
            ]
        )

    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :business, true)"),
            {"business": str(business)},
        )
        session.add(
            CustomerContactModel(
                id=uuid4(),
                business_id=business,
                customer_id=customer.id,
                kind="email",
                value="b@example.org",
                is_primary=True,
                created_at=datetime.now(UTC),
            )
        )
        with pytest.raises(IntegrityError):
            await session.flush()

    async with postgres_sessions() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :business, true)"),
            {"business": str(business)},
        )
        now = datetime.now(UTC)
        session.add(
            CustomerExternalIdentityModel(
                id=uuid4(),
                business_id=business,
                customer_id=customer.id,
                provider="telegram",
                channel_account_id="channel",
                external_user_id="user",
                status="active",
                linked_at=now,
                verification_method="provider_assertion",
                verified_at=now,
            )
        )
        with pytest.raises(IntegrityError):
            await session.flush()
