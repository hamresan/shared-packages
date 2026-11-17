"""End-to-end ASGI route tests with trusted host-supplied actor context."""

from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from customer import CreateCustomerCommand, ExternalIdentityKey, LinkExternalIdentityCommand
from customer.application.actor import CustomerActor
from customer.presentation.http import create_customer_router
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.external_evidence import FakeExternalEvidenceVerifier
from tests.support.http_asgi import request_asgi


async def test_http_create_retry_and_version_conflict() -> None:
    module, uow = build_customer_module()
    business = uuid4()
    actor = build_actor(business)

    async def authenticate(authorization: str | None = Header(default=None)) -> CustomerActor:
        if authorization != "Bearer trusted":
            raise HTTPException(status_code=401, detail="unauthorized")
        return actor

    app = FastAPI()
    app.include_router(create_customer_router(module, authenticate))
    base = f"/businesses/{business}/customers"
    auth = {"authorization": "Bearer trusted", "idempotency-key": "same-operation"}

    missing, _ = await request_asgi(app, "POST", base, payload={"display_name": "A"})
    assert missing == 401

    first_status, first = await request_asgi(
        app, "POST", base, payload={"display_name": "Ada"}, headers=auth
    )
    retry_status, retry = await request_asgi(
        app, "POST", base, payload={"display_name": "Ada"}, headers=auth
    )
    assert (first_status, retry_status) == (201, 201)
    assert first == retry
    assert set(first) == {
        "id",
        "business_id",
        "display_name",
        "status",
        "version",
        "created_at",
        "updated_at",
    }
    assert len(uow.customers.records) == 1

    forged_status, _ = await request_asgi(
        app,
        "POST",
        base,
        payload={"display_name": "Mallory", "actor_id": str(uuid4())},
        headers=auth,
    )
    assert forged_status == 422
    assert len(uow.customers.records) == 1

    stale_status, stale = await request_asgi(
        app,
        "PATCH",
        f"{base}/{first['id']}",
        payload={"display_name": "Changed", "expected_version": 10},
        headers=auth,
    )
    assert (stale_status, stale["detail"]) == (409, "version_conflict")


async def test_http_masks_foreign_business_and_does_not_auto_create_from_lookup() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())

    async def authenticate() -> CustomerActor:
        return actor

    app = FastAPI()
    app.include_router(create_customer_router(module, authenticate))
    base = f"/businesses/{uuid4()}/customers"
    status, body = await request_asgi(app, "GET", f"{base}/{uuid4()}")
    assert (status, body["detail"]) == (404, "customer_unavailable")

    status, body = await request_asgi(
        app,
        "POST",
        f"{base}/identities/resolve",
        payload={"provider": "whatsapp", "channel_account_id": "one", "external_user_id": "two"},
    )
    assert (status, body["detail"]) == (404, "customer_unavailable")
    assert not uow.customers.records


async def test_http_resolves_only_verified_minimal_identity_projection() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor, "Alex")
    )
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot-1", "sender-1")
    verifier = module.config.external_evidence_verifier
    assert isinstance(verifier, FakeExternalEvidenceVerifier)
    verifier.register("trusted-proof", key)
    await module.external_identities.link.execute(
        LinkExternalIdentityCommand(actor, key, customer.id, "trusted-proof")
    )

    async def authenticate() -> CustomerActor:
        return actor

    app = FastAPI()
    app.include_router(create_customer_router(module, authenticate))
    status, body = await request_asgi(
        app,
        "POST",
        f"/businesses/{actor.business_id}/customers/identities/resolve",
        payload={
            "provider": key.provider,
            "channel_account_id": key.channel_account_id,
            "external_user_id": key.external_user_id,
        },
    )
    assert status == 200
    assert body["customer_id"] == str(customer.id)
    assert set(body) == {
        "customer_id",
        "business_id",
        "display_name",
        "identity_status",
        "verification_method",
        "verified_at",
    }
