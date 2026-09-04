"""Stage 10 messaging webhook host-dispatch tests."""

import asyncio
import hashlib
import hmac

from instagram_api.application.webhooks import (\n    InstagramWebhookProcessor,\n    NullInstagramWebhookOperationalObserver,\n    RetryInstagramWebhookFailureHandler,\n)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramMessageReceived,
)
from instagram_api.infrastructure.meta.webhooks import MetaInstagramWebhookSignatureVerifier
from tests.fakes import (
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
)
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_inbound_dm_reaches_host_with_resolved_connection_context() -> None:
    payload = (
        b'{"entry":[{"id":"account-a","time":1788523200,"messaging":['
        b'{"sender":{"id":"customer"},"recipient":{"id":"account-a"},'
        b'"timestamp":1788523200123,"message":{"mid":"message-1","text":"hello"}}]}]}'
    )
    dispatcher = FakeInstagramWebhookEventDispatcher()
    processor = InstagramWebhookProcessor(
        MetaInstagramWebhookSignatureVerifier("secret"),
        build_meta_webhook_parser(),
        FakeInstagramWebhookIdempotencyStore(),
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account-a"): InstagramConnectionId("connection-a")}
        ),
        dispatcher,
        RetryInstagramWebhookFailureHandler(),
        NullInstagramWebhookOperationalObserver(),
    )
    signature = (
        "sha256="
        + hmac.new(
            b"secret",
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    dispatched = asyncio.run(processor.process(payload, signature))

    assert dispatched == 1
    assert len(dispatcher.events) == 1
    connection_id, event = dispatcher.events[0]
    assert connection_id == InstagramConnectionId("connection-a")
    assert isinstance(event.payload, InstagramMessageReceived)
    assert event.payload.text == "hello"
