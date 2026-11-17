from uuid import uuid4

import pytest

from customer.application.models import (
    CreateCustomerCommand,
    CustomerMutationCommand,
    GetCustomerQuery,
    UpdateCustomerCommand,
)
from customer.domain import (
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerStatus,
    CustomerVersionConflictError,
)
from tests.support.factories.customer_module import build_actor, build_customer_module


async def test_update_archive_reactivate_with_optimistic_locking() -> None:
    module, _ = build_customer_module()
    business_id = uuid4()
    actor = build_actor(business_id)
    customer = await module.customers.create.execute(CreateCustomerCommand(business_id, actor))
    updated = await module.customers.update.execute(
        UpdateCustomerCommand(business_id, actor, customer.id, 1, "  New   Name  ")
    )
    assert updated.display_name == "New Name"
    assert updated.version == 2
    with pytest.raises(CustomerVersionConflictError):
        await module.customers.update.execute(
            UpdateCustomerCommand(business_id, actor, customer.id, 1, "Stale")
        )

    archived = await module.customers.archive.execute(
        CustomerMutationCommand(business_id, actor, customer.id, 2)
    )
    assert archived.status is CustomerStatus.ARCHIVED
    with pytest.raises(CustomerInvalidStateError):
        await module.customers.archive.execute(
            CustomerMutationCommand(business_id, actor, customer.id, 3)
        )
    reactivated = await module.customers.reactivate.execute(
        CustomerMutationCommand(business_id, actor, customer.id, 3)
    )
    assert (reactivated.status, reactivated.version) == (CustomerStatus.ACTIVE, 4)
    retrieved = await module.customers.get.execute(
        GetCustomerQuery(business_id, actor, customer.id)
    )
    assert retrieved == reactivated


async def test_missing_customer_and_foreign_tenant_not_found() -> None:
    module, _ = build_customer_module()
    business_a = uuid4()
    business_b = uuid4()
    actor_a = build_actor(business_a)
    actor_b = build_actor(business_b)
    customer = await module.customers.create.execute(CreateCustomerCommand(business_a, actor_a))
    with pytest.raises(CustomerNotFoundError):
        await module.customers.get.execute(GetCustomerQuery(business_b, actor_b, customer.id))
    with pytest.raises(CustomerNotFoundError):
        await module.customers.update.execute(
            UpdateCustomerCommand(business_b, actor_b, customer.id, 1, "Other")
        )
    with pytest.raises(CustomerNotFoundError):
        await module.customers.archive.execute(
            CustomerMutationCommand(business_b, actor_b, customer.id, 1)
        )
    with pytest.raises(CustomerNotFoundError):
        await module.customers.reactivate.execute(
            CustomerMutationCommand(business_b, actor_b, customer.id, 1)
        )


async def test_concurrent_versions_reject_later_writer() -> None:
    module, _ = build_customer_module()
    business = uuid4()
    actor = build_actor(business)
    customer = await module.customers.create.execute(
        CreateCustomerCommand(business, actor, "First")
    )
    await module.customers.update.execute(
        UpdateCustomerCommand(business, actor, customer.id, 1, "Second")
    )
    with pytest.raises(CustomerVersionConflictError):
        await module.customers.archive.execute(
            CustomerMutationCommand(business, actor, customer.id, 1)
        )
    with pytest.raises(CustomerVersionConflictError):
        await module.customers.reactivate.execute(
            CustomerMutationCommand(business, actor, customer.id, 1)
        )
