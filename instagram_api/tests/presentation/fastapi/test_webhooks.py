"""FastAPI Instagram webhook adapter tests."""

import hashlib
import hmac

from fastapi import FastAPI
from fastapi.testclient import TestClient

from instagram_api.application.webhooks import (
    InstagramWebhookHandshakeService,
    InstagramWebhookProcessor,
)
from instagram_api.domain import InstagramAccountId, InstagramConnectionId
from instagram_api.presentation.fastapi import create_instagram_webhook_router
from instagram_api.infrastructure.meta.webhooks import (
    MetaInstagramWebhookEventIdFactory,
    MetaInstagramWebhookEventMapper,
    MetaInstagramWebhookFieldParser,
    MetaInstagramWebhookParser,
    MetaInstagramWebhookSignatureVerifier,
)
from tests.fakes import (
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
)


def build_client() -> tuple[TestClient, FakeInstagramWebhookEventDispatcher]:
    secret = "app-secret"
    dispatcher = FakeInstagramWebhookEventDispatcher()
    processor = InstagramWebhookProcessor(
        MetaInstagramWebhookSignatureVerifier(secret),
        MetaInstagramWebhookParser(
            MetaInstagramWebhookFieldParser(),
            MetaInstagramWebhookEventMapper(
                MetaInstagramWebhookEventIdFactory()
            ),
        ),
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
    return TestClient(app), dispatcher


def test_fastapi_adapter_handles_verification_handshake() -> None:
    client, _ = build_client()

    response = client.get(
        "/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "verify-token",
            "hub.challenge": "12345",
        },
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_fastapi_adapter_rejects_invalid_handshake() -> None:
    client, _ = build_client()

    response = client.get(
        "/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "12345",
        },
    )

    assert response.status_code == 403


def test_fastapi_adapter_verifies_and_dispatches_post_delivery() -> None:
    client, dispatcher = build_client()
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"changes":[{"field":"comments","value":{"id":"comment"}}]}]}'
    )
    digest = hmac.new(b"app-secret", payload, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhooks/instagram",
        content=payload,
        headers={"X-Hub-Signature-256": f"sha256={digest}"},
    )

    assert response.status_code == 200
    assert response.json() == {"dispatched": 1}
    assert dispatcher.events[0][0] == InstagramConnectionId("connection")


def test_fastapi_adapter_rejects_unauthentic_post() -> None:
    client, dispatcher = build_client()

    response = client.post(
        "/webhooks/instagram",
        content=b'{"entry":[]}',
        headers={"X-Hub-Signature-256": "sha256=wrong"},
    )

    assert response.status_code == 403
    assert dispatcher.events == []
