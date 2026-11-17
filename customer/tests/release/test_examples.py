"""Ensure public documentation examples execute against the facade."""

from uuid import uuid4

from fastapi import FastAPI

from customer import ExternalIdentityKey, LinkExternalIdentityCommand
from examples.guest_lifecycle import create_guest_and_read
from examples.http_router import mount_customer_api
from examples.identity_lookup import resolve_verified_identity
from examples.profile_details import save_contact_and_language
from examples.version_conflict import rename_if_unchanged
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.external_evidence import FakeExternalEvidenceVerifier


async def test_guest_lifecycle_example_is_idempotent_and_authorized() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())
    created, profile = await create_guest_and_read(module, actor, "sample-operation")
    repeated, _ = await create_guest_and_read(module, actor, "sample-operation")
    assert created == profile == repeated
    assert len(uow.customers.records) == 1


def test_fastapi_composition_example_mounts_routes() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    app = FastAPI()
    mount_customer_api(app, module, lambda: actor)
    assert any(path.endswith("/identities/resolve") for path in app.openapi()["paths"])


async def test_profile_and_identity_examples_enforce_verified_lookup() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    created, _ = await create_guest_and_read(module, actor, "details-example")
    contact, preference = await save_contact_and_language(module, actor, created.id)
    assert contact.is_verified is False
    assert preference.value == "en"

    unresolved = await resolve_verified_identity(module, actor, "telegram", "bot", "user")
    assert unresolved is None
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot", "user")
    evidence = module.config.external_evidence_verifier
    assert isinstance(evidence, FakeExternalEvidenceVerifier)
    evidence.register("verified-proof", key)
    await module.external_identities.link.execute(
        LinkExternalIdentityCommand(actor, key, created.id, "verified-proof")
    )
    resolved = await resolve_verified_identity(module, actor, "telegram", "bot", "user")
    assert resolved is not None and resolved.customer_id == created.id
    assert not hasattr(resolved, "notes")


async def test_version_conflict_example_returns_false_on_stale_update() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    created, _ = await create_guest_and_read(module, actor, "version-example")
    assert await rename_if_unchanged(module, actor, created.id, created.version)
    assert not await rename_if_unchanged(module, actor, created.id, created.version)
