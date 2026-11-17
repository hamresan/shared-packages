from uuid import uuid4

import pytest

from customer import CustomerModule, CustomerModuleConfig
from customer.application.models import CreateCustomerCommand, GetCustomerQuery
from customer.domain import (
    CustomerIdempotencyConflictError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
)
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.authorization import DenyCustomerAuthorizer


async def test_guest_creation_normalizes_name_and_replays_idempotently() -> None:
    module, uow = build_customer_module()
    business_id = uuid4()
    actor = build_actor(business_id)
    command = CreateCustomerCommand(business_id, actor, "  Ada   Lovelace ", "request-42")
    created = await module.customers.create.execute(command)
    replay = await module.customers.create.execute(command)
    assert replay == created
    assert created.display_name == "Ada Lovelace"
    assert len(uow.customers.records) == len(uow.idempotency.records) == 1

    guest = await module.customers.create.execute(CreateCustomerCommand(business_id, actor))
    assert guest.display_name is None
    assert guest.id != created.id
    retrieved = await module.customers.get.execute(GetCustomerQuery(business_id, actor, guest.id))
    assert retrieved == guest


async def test_idempotency_mismatch_rejected_without_duplicate() -> None:
    module, uow = build_customer_module()
    business_id = uuid4()
    actor = build_actor(business_id)
    await module.customers.create.execute(CreateCustomerCommand(business_id, actor, "Ada", "key"))
    with pytest.raises(CustomerIdempotencyConflictError):
        await module.customers.create.execute(
            CreateCustomerCommand(business_id, actor, "Bob", "key")
        )
    assert len(uow.customers.records) == 1


async def test_idempotency_record_with_missing_customer_fails_closed() -> None:
    module, uow = build_customer_module()
    business = uuid4()
    actor = build_actor(business)
    command = CreateCustomerCommand(business, actor, "Ada", "saved-key")
    created = await module.customers.create.execute(command)
    del uow.customers.records[(business, created.id)]
    with pytest.raises(CustomerNotFoundError):
        await module.customers.create.execute(command)


async def test_cross_business_scope_fails_before_access() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    foreign_business = uuid4()
    with pytest.raises(CustomerPermissionDeniedError):
        await module.customers.create.execute(CreateCustomerCommand(foreign_business, actor))
    with pytest.raises(CustomerPermissionDeniedError):
        await module.customers.get.execute(GetCustomerQuery(foreign_business, actor, uuid4()))
    with pytest.raises(CustomerNotFoundError):
        await module.customers.get.execute(GetCustomerQuery(actor.business_id, actor, uuid4()))


@pytest.mark.parametrize("key", ["", "x" * 201])
async def test_invalid_idempotency_key_rejected(key: str) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    with pytest.raises(CustomerValidationError):
        await module.customers.create.execute(
            CreateCustomerCommand(actor.business_id, actor, "A", key)
        )


async def test_overlong_name_is_rejected() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    with pytest.raises(CustomerValidationError):
        await module.customers.create.execute(
            CreateCustomerCommand(actor.business_id, actor, "a" * 201)
        )


async def test_host_authorization_is_enforced_before_mutation() -> None:
    module, uow = build_customer_module()
    denied = CustomerModule(
        CustomerModuleConfig(
            uow,
            DenyCustomerAuthorizer(),
            module.config.identity_verifier,
            module.config.clock,
            module.config.identifiers,
            module.config.creation_fingerprinter,
        )
    )
    actor = build_actor(uuid4())
    with pytest.raises(CustomerPermissionDeniedError):
        await denied.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    assert not uow.customers.records
