from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from customer import (
    CreateCustomerCommand,
    CustomerIdentityConflictError,
    CustomerIdentityVerificationError,
    CustomerModule,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
    ExternalIdentityKey,
    FindExternalIdentityQuery,
    GetOrCreateExternalIdentityCommand,
    LinkExternalIdentityCommand,
    RecordExternalIdentityVerificationCommand,
    RevokeExternalIdentityCommand,
)
from customer.domain.external_identity import ExternalIdentityStatus
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.external_evidence import FakeExternalEvidenceVerifier


def verified_evidence(module: CustomerModule, key: ExternalIdentityKey, reference: str) -> None:
    verifier = module.config.external_evidence_verifier
    assert isinstance(verifier, FakeExternalEvidenceVerifier)
    verifier.register(reference, key)


async def test_external_link_requires_verified_evidence_and_is_namespace_scoped() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    key = ExternalIdentityKey(actor.business_id, "TELEGRAM", "bot-1", "sender-42")
    command = LinkExternalIdentityCommand(actor, key, customer.id, "proof-1")
    with pytest.raises(CustomerIdentityVerificationError):
        await module.external_identities.link.execute(command)
    assert not uow.external_identities.identities
    normalized = ExternalIdentityKey(actor.business_id, "telegram", "bot-1", "sender-42")
    verified_evidence(module, normalized, "proof-1")
    linked = await module.external_identities.link.execute(command)
    assert linked.customer_id == customer.id
    assert linked.identity_status is ExternalIdentityStatus.ACTIVE
    assert linked.verification_method == "provider_assertion"
    assert not hasattr(linked, "contacts")
    resolved = await module.external_identities.find.execute(FindExternalIdentityQuery(actor, key))
    assert resolved == linked
    assert (
        await module.external_identities.find.execute(
            FindExternalIdentityQuery(
                actor, ExternalIdentityKey(actor.business_id, "telegram", "bot-2", "sender-42")
            )
        )
        is None
    )
    assert (
        await module.external_identities.find.execute(
            FindExternalIdentityQuery(
                actor, ExternalIdentityKey(actor.business_id, "telegram", "bot-1", "sender-99")
            )
        )
        is None
    )


async def test_get_or_create_deduplicates_retries_without_cross_business_sharing() -> None:
    module, uow = build_customer_module()
    actor_a, actor_b = build_actor(uuid4()), build_actor(uuid4())
    key_a = ExternalIdentityKey(actor_a.business_id, "whatsapp", "business-account", "123")
    key_b = ExternalIdentityKey(actor_b.business_id, "whatsapp", "business-account", "123")
    verified_evidence(module, key_a, "assert-a")
    verified_evidence(module, key_b, "assert-b")
    command = GetOrCreateExternalIdentityCommand(actor_a, key_a, "assert-a", "Alice")
    first = await module.external_identities.get_or_create.execute(command)
    replay = await module.external_identities.get_or_create.execute(command)
    second_business = await module.external_identities.get_or_create.execute(
        GetOrCreateExternalIdentityCommand(actor_b, key_b, "assert-b", "Alice")
    )
    assert first == replay
    assert first.customer_id != second_business.customer_id
    assert len(uow.customers.records) == 2
    assert len(uow.external_identities.identities) == 2


async def test_revoke_and_relink_to_another_customer_requires_new_evidence() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    first_customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    second_customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot", "user-77")
    verified_evidence(module, key, "first-proof")
    await module.external_identities.link.execute(
        LinkExternalIdentityCommand(actor, key, first_customer.id, "first-proof")
    )
    with pytest.raises(CustomerIdentityConflictError):
        await module.external_identities.link.execute(
            LinkExternalIdentityCommand(actor, key, second_customer.id, "first-proof")
        )
    with pytest.raises(CustomerIdentityConflictError):
        await module.external_identities.relink.execute(
            LinkExternalIdentityCommand(actor, key, second_customer.id, "first-proof")
        )
    await module.external_identities.revoke.execute(
        RevokeExternalIdentityCommand(actor, key, first_customer.id)
    )
    unresolved = await module.external_identities.find.execute(
        FindExternalIdentityQuery(actor, key)
    )
    assert unresolved is None
    with pytest.raises(CustomerIdentityVerificationError):
        await module.external_identities.relink.execute(
            LinkExternalIdentityCommand(actor, key, second_customer.id, "new-proof")
        )
    with pytest.raises(CustomerIdentityVerificationError):
        await module.external_identities.relink.execute(
            LinkExternalIdentityCommand(actor, key, second_customer.id, "first-proof")
        )
    verifier = module.config.external_evidence_verifier
    assert isinstance(verifier, FakeExternalEvidenceVerifier)
    verifier.register(
        "new-proof",
        key,
        verified_at=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=1),
    )
    moved = await module.external_identities.relink.execute(
        LinkExternalIdentityCommand(actor, key, second_customer.id, "new-proof")
    )
    assert moved.customer_id == second_customer.id


async def test_verification_provenance_can_be_refreshed_only_on_active_link() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    key = ExternalIdentityKey(actor.business_id, "instagram", "account", "user")
    verified_evidence(module, key, "proof")
    await module.external_identities.link.execute(
        LinkExternalIdentityCommand(actor, key, customer.id, "proof")
    )
    refreshed = await module.external_identities.record_verification.execute(
        RecordExternalIdentityVerificationCommand(actor, key, customer.id, "proof")
    )
    assert refreshed.customer_id == customer.id
    await module.external_identities.revoke.execute(
        RevokeExternalIdentityCommand(actor, key, customer.id)
    )
    with pytest.raises(CustomerNotFoundError):
        await module.external_identities.record_verification.execute(
            RecordExternalIdentityVerificationCommand(actor, key, customer.id, "proof")
        )


async def test_external_lookup_scope_checks_trusted_actor() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    other = build_actor(uuid4())
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot", "subject")
    with pytest.raises(CustomerPermissionDeniedError):
        await module.external_identities.find.execute(FindExternalIdentityQuery(other, key))


async def test_valid_evidence_cannot_be_reused_for_another_namespace() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    original = ExternalIdentityKey(actor.business_id, "telegram", "bot-a", "sender")
    substituted = ExternalIdentityKey(actor.business_id, "telegram", "bot-b", "sender")
    verified_evidence(module, original, "valid-for-a")
    with pytest.raises(CustomerIdentityVerificationError):
        await module.external_identities.link.execute(
            LinkExternalIdentityCommand(actor, substituted, customer.id, "valid-for-a")
        )


@pytest.mark.parametrize("method,verified_at", [("", None), ("challenge", datetime(2026, 1, 1))])
async def test_external_evidence_must_have_method_and_aware_time(
    method: str, verified_at: datetime | None
) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    key = ExternalIdentityKey(actor.business_id, "whatsapp", "account", "sender")
    verifier = module.config.external_evidence_verifier
    assert isinstance(verifier, FakeExternalEvidenceVerifier)
    verifier.register("proof", key, method, verified_at)
    with pytest.raises(CustomerIdentityVerificationError):
        await module.external_identities.get_or_create.execute(
            GetOrCreateExternalIdentityCommand(actor, key, "proof")
        )


@pytest.mark.parametrize(
    "provider,account,subject",
    [
        ("", "account", "subject"),
        ("bad provider!", "account", "subject"),
        ("telegram", "", "subject"),
        ("telegram", "account", ""),
    ],
)
async def test_external_identity_key_validation(provider: str, account: str, subject: str) -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    with pytest.raises(CustomerValidationError):
        await module.external_identities.find.execute(
            FindExternalIdentityQuery(
                actor, ExternalIdentityKey(actor.business_id, provider, account, subject)
            )
        )


async def test_linking_same_active_external_identity_refreshes_provenance() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot", "sender")
    verified_evidence(module, key, "proof")
    command = LinkExternalIdentityCommand(actor, key, customer.id, "proof")
    first = await module.external_identities.link.execute(command)
    second = await module.external_identities.link.execute(command)
    assert first == second
    assert len(uow.external_identities.identities) == 1
