from uuid import uuid4

import pytest

from customer import (
    CreateCustomerCommand,
    CustomerDetailsQuery,
    CustomerIdentityConflictError,
    CustomerIdentityVerificationError,
    CustomerModule,
    CustomerModuleConfig,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    LinkInternalIdentityCommand,
    ResolveInternalIdentityQuery,
)
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.identity_verification import RejectIdentityVerifier


async def test_internal_identity_is_optional_business_scoped_and_idempotent() -> None:
    module, _ = build_customer_module()
    identity_user_id = uuid4()
    actor_a = build_actor(uuid4())
    actor_b = build_actor(uuid4())
    customer_a = await module.customers.create.execute(
        CreateCustomerCommand(actor_a.business_id, actor_a)
    )
    customer_b = await module.customers.create.execute(
        CreateCustomerCommand(actor_b.business_id, actor_b)
    )
    command_a = LinkInternalIdentityCommand(
        actor_a.business_id, actor_a, customer_a.id, identity_user_id
    )
    linked_a = await module.identities.link.execute(command_a)
    assert linked_a.customer_id == customer_a.id
    assert await module.identities.link.execute(command_a) == linked_a
    linked_b = await module.identities.link.execute(
        LinkInternalIdentityCommand(actor_b.business_id, actor_b, customer_b.id, identity_user_id)
    )
    assert linked_b.customer_id == customer_b.id
    assert linked_a.customer_id != linked_b.customer_id
    assert (
        await module.identities.resolve.execute(
            ResolveInternalIdentityQuery(actor_a.business_id, actor_a, identity_user_id)
        )
        == linked_a
    )


async def test_internal_link_conflicts_and_revocation() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    first = await module.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    second = await module.customers.create.execute(CreateCustomerCommand(actor.business_id, actor))
    user_a, user_b = uuid4(), uuid4()
    await module.identities.link.execute(
        LinkInternalIdentityCommand(actor.business_id, actor, first.id, user_a)
    )
    with pytest.raises(CustomerIdentityConflictError):
        await module.identities.link.execute(
            LinkInternalIdentityCommand(actor.business_id, actor, second.id, user_a)
        )
    with pytest.raises(CustomerIdentityConflictError):
        await module.identities.link.execute(
            LinkInternalIdentityCommand(actor.business_id, actor, first.id, user_b)
        )
    with pytest.raises(CustomerNotFoundError):
        await module.identities.link.execute(
            LinkInternalIdentityCommand(actor.business_id, actor, uuid4(), user_b)
        )
    await module.identities.unlink.execute(CustomerDetailsQuery(actor.business_id, actor, first.id))
    assert (
        await module.identities.resolve.execute(
            ResolveInternalIdentityQuery(actor.business_id, actor, user_a)
        )
        is None
    )
    with pytest.raises(CustomerNotFoundError):
        await module.identities.unlink.execute(
            CustomerDetailsQuery(actor.business_id, actor, first.id)
        )
    await module.identities.link.execute(
        LinkInternalIdentityCommand(actor.business_id, actor, second.id, user_a)
    )


async def test_internal_lookup_does_not_cross_tenant() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    foreign_actor = build_actor(uuid4())
    with pytest.raises(CustomerPermissionDeniedError):
        await module.identities.resolve.execute(
            ResolveInternalIdentityQuery(actor.business_id, foreign_actor, uuid4())
        )


async def test_internal_link_rejects_invalid_user_without_side_effects() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    restricted = CustomerModule(
        CustomerModuleConfig(
            uow,
            module.config.authorizer,
            RejectIdentityVerifier(),
            module.config.clock,
            module.config.identifiers,
            module.config.creation_fingerprinter,
            module.config.external_evidence_verifier,
        )
    )
    with pytest.raises(CustomerIdentityVerificationError):
        await restricted.identities.link.execute(
            LinkInternalIdentityCommand(actor.business_id, actor, customer.id, uuid4())
        )
    assert not uow.internal_identities.links
