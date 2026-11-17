"""End-to-end ASGI route tests with trusted host-supplied actor context."""

from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from customer.application.actor import CustomerActor
from customer.presentation.http import create_customer_router
from tests.support.factories.customer_module import build_actor, build_customer_module
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
