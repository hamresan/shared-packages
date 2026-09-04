"""Stage 11 comment webhook connection-routing tests."""

import asyncio
import hashlib
import hmac

from instagram_api.application.webhooks import InstagramWebhookProcessor
from instagram_api.domain import (
    InstagramAccountId,
    InstagramCommentCreated,
    InstagramConnectionId,
)
from instagram_api.infrastructure.meta.webhooks import MetaInstagramWebhookSignatureVerifier
from tests.fakes import (
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
)
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_comment_event_reaches_host_with_resolved_connection_context() -> None:
    payload = (
        b'{"entry":[{"id":"account-a","time":1788523200,'
        b'"field":"comments","value":{"id":"comment","text":"hello",'
        b'"media":{"id":"media"}}}]}'
    )
    dispatcher = FakeInstagramWebhookEventDispatcher()
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
        dispatcher,
    )
    signature = "sha256=" + hmac.new(
        b"secret",
        payload,
        hashlib.sha256,
    ).hexdigest()

    dispatched = asyncio.run(processor.process(payload, signature))

    assert dispatched == 1
    connection_id, event = dispatcher.events[0]
    assert connection_id == InstagramConnectionId("connection-a")
    assert isinstance(event.payload, InstagramCommentCreated)
    assert event.payload.comment_id == "comment"
