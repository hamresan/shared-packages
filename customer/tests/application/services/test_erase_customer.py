from dataclasses import replace
from uuid import uuid4

import pytest

from customer import CustomerModule
from customer.application.models import CreateCustomerCommand, CustomerMutationCommand
from customer.domain import CustomerErasedError, CustomerPermissionDeniedError, CustomerStatus
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.erasure_policy import AllowErasurePolicy, DenyErasurePolicy


async def test_erasure_requires_explicit_host_policy() -> None:
    module, uow = build_customer_module()
    business = uuid4()
    actor = build_actor(business)
    customer = await module.customers.create.execute(CreateCustomerCommand(business, actor, "Ada"))
    with pytest.raises(CustomerPermissionDeniedError):
        await module.customers.erase.execute(
            CustomerMutationCommand(business, actor, customer.id, 1)
        )
    assert uow.customers.records[(business, customer.id)].status is CustomerStatus.ACTIVE


async def test_retention_hold_prevents_erasure() -> None:
    module, uow = build_customer_module()
    module = CustomerModule(replace(module.config, erasure_policy=DenyErasurePolicy()))
    business = uuid4()
    actor = build_actor(business)
    customer = await module.customers.create.execute(CreateCustomerCommand(business, actor, "Ada"))
    with pytest.raises(CustomerPermissionDeniedError):
        await module.customers.erase.execute(
            CustomerMutationCommand(business, actor, customer.id, 1)
        )
    assert len(uow.audit.events) == 1


async def test_erasure_is_terminal_and_audited() -> None:
    module, uow = build_customer_module()
    module = CustomerModule(replace(module.config, erasure_policy=AllowErasurePolicy()))
    business = uuid4()
    actor = build_actor(business)
    customer = await module.customers.create.execute(
        CreateCustomerCommand(business, actor, "Ada", "creation-key")
    )
    erased = await module.customers.erase.execute(
        CustomerMutationCommand(business, actor, customer.id, 1)
    )
    assert erased.status is CustomerStatus.ERASED
    assert erased.display_name is None
    assert erased.version == 2
    assert uow.idempotency.records == {}
    assert [event.action for event in uow.audit.events] == ["customer.create", "customer.erase"]
    with pytest.raises(CustomerErasedError):
        await module.customers.reactivate.execute(
            CustomerMutationCommand(business, actor, customer.id, 2)
        )
