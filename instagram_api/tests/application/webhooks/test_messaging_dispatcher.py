"""Stage 10 messaging webhook host-dispatch tests."""

import asyncio

from instagram_api.application.webhooks import (
    InstagramMessagingWebhookDispatcher,
    InstagramWebhookProcessor,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramMessageReceived,
)
from instagram_api.infrastructure.meta.webhooks import (
    MetaInstagramWebhookSignatureVerifier,
)
from tests.fakes import (
    FakeInstagramMessagingWebhookHandler,
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookIdempotencyStore,
)
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_inbound_dm_reaches_host_with_resolved_connection_context() -> None:
    payload = (
        b'{"entry":[{"id":"account-a","time":1788523200,"messaging":['
        b'{"sender":{"id":"customer"},"recipient":{"id":"account-a"},'
        b'"timestamp":1788523200123,"message":{"mid":"message-1","text":"hello"}}]}]}'
    )
    handler = FakeInstagramMessagingWebhookHandler()
    processor = InstagramWebhookProcessor(
        MetaInstagramWebhookSignatureVerifier("secret"),
        build_meta_webhook_parser(),
        FakeInstagramWebhookIdempotencyStore(),
        FakeInstagramWebhookConnectionResolver(
            {
                InstagramAccountId("account-a"): InstagramConnectionId(
                    "connection-a"
                )
            }
        ),
        InstagramMessagingWebhookDispatcher(handler),
    )

    import hashlib
    import hmac

    signature = "sha256=" + hmac.new(
        b"secret",
        payload,
        hashlib.sha256,
    ).hexdigest()

    dispatched = asyncio.run(processor.process(payload, signature))

    assert dispatched == 1
    assert len(handler.events) == 1
    connection_id, normalized = handler.events[0]
    assert connection_id == InstagramConnectionId("connection-a")
    assert isinstance(normalized, InstagramMessageReceived)
    assert normalized.text == "hello"


def test_messaging_dispatcher_ignores_generic_non_messaging_payload() -> None:
    handler = FakeInstagramMessagingWebhookHandler()
    dispatcher = InstagramMessagingWebhookDispatcher(handler)
    event = build_meta_webhook_parser().parse(
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"changes":[{"field":"comments","value":{"id":"comment"}}]}]}'
    )[0]

    asyncio.run(
        dispatcher.dispatch(
            InstagramConnectionId("connection"),
            event,
        )
    )

    assert handler.events == []
