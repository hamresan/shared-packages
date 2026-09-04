"""FastAPI Instagram webhook adapter tests."""

import asyncio
import hashlib
import hmac

import httpx
from fastapi import FastAPI

from instagram_api.application.webhooks import (
    InstagramWebhookHandshakeService,
    InstagramWebhookProcessor,
)
from instagram_api.domain import InstagramAccountId, InstagramConnectionId
from instagram_api.infrastructure.meta.webhooks import MetaInstagramWebhookSignatureVerifier
from instagram_api.presentation.fastapi import create_instagram_webhook_router
from tests.fakes import (
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
)


def build_app() -> tuple[FastAPI, FakeInstagramWebhookEventDispatcher]:
    secret = "app-secret"
    dispatcher = FakeInstagramWebhookEventDispatcher()
    processor = InstagramWebhookProcessor(
        MetaInstagramWebhookSignatureVerifier(secret),
        build_meta_webhook_parser(),
        FakeInstagramWebhookIdempotencyStore(),
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account"): InstagramConnectionId("connection")}
        ),
        dispatcher,
    )
    app = FastAPI()
    app.include_router(
        create_instagram_webhook_router(
            InstagramWebhookHandshakeService("verify-token"),
            processor,
        )
    )
    return app, dispatcher


async def get_response(
    app: FastAPI,
    *,
    params: dict[str, str],
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get("/webhooks/instagram", params=params)


async def post_response(
    app: FastAPI,
    *,
    content: bytes,
    signature: str,
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.post(
            "/webhooks/instagram",
            content=content,
            headers={"X-Hub-Signature-256": signature},
        )


def test_fastapi_adapter_handles_verification_handshake() -> None:
    app, _ = build_app()

    response = asyncio.run(
        get_response(
            app,
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "verify-token",
                "hub.challenge": "12345",
            },
        )
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_fastapi_adapter_rejects_invalid_handshake() -> None:
    app, _ = build_app()

    response = asyncio.run(
        get_response(
            app,
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong",
                "hub.challenge": "12345",
            },
        )
    )

    assert response.status_code == 403


def test_fastapi_adapter_verifies_and_dispatches_post_delivery() -> None:
    app, dispatcher = build_app()
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"changes":[{"field":"comments","value":{"id":"comment"}}]}]}'
    )
    digest = hmac.new(b"app-secret", payload, hashlib.sha256).hexdigest()

    response = asyncio.run(
        post_response(
            app,
            content=payload,
            signature=f"sha256={digest}",
        )
    )

    assert response.status_code == 200
    assert response.json() == {"dispatched": 1}
    assert dispatcher.events[0][0] == InstagramConnectionId("connection")


def test_fastapi_adapter_rejects_unauthentic_post() -> None:
    app, dispatcher = build_app()

    response = asyncio.run(
        post_response(
            app,
            content=b'{"entry":[]}',
            signature="sha256=wrong",
        )
    )

    assert response.status_code == 403
    assert dispatcher.events == []
