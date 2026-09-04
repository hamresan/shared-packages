"""Instagram webhook processor tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.webhooks import (
    InstagramWebhookAuthenticationError,
    InstagramWebhookProcessor,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramWebhookEvent,
)
from tests.fakes import (
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
    FakeInstagramWebhookParser,
    FakeInstagramWebhookVerifier,
)


def build_event(
    event_id: str,
    account_id: str,
) -> InstagramWebhookEvent:
    return InstagramWebhookEvent(
        event_id=event_id,
        event_type="generic",
        provider_account_id=InstagramAccountId(account_id),
        occurred_at=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
    )


def test_processor_rejects_unauthentic_delivery_before_parsing() -> None:
    parser = FakeInstagramWebhookParser((build_event("event", "account"),))
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(False),
        parser,
        FakeInstagramWebhookIdempotencyStore(),
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account"): InstagramConnectionId("connection")}
        ),
        FakeInstagramWebhookEventDispatcher(),
    )

    with pytest.raises(InstagramWebhookAuthenticationError):
        asyncio.run(processor.process(b"payload", "signature"))


def test_processor_routes_multiple_accounts_and_suppresses_duplicate_event() -> None:
    first = build_event("event-a", "account-a")
    duplicate = build_event("event-a", "account-a")
    second = build_event("event-b", "account-b")
    store = FakeInstagramWebhookIdempotencyStore()
    resolver = FakeInstagramWebhookConnectionResolver(
        {
            InstagramAccountId("account-a"): InstagramConnectionId("connection-a"),
            InstagramAccountId("account-b"): InstagramConnectionId("connection-b"),
        }
    )
    dispatcher = FakeInstagramWebhookEventDispatcher()
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(True),
        FakeInstagramWebhookParser((first, duplicate, second)),
        store,
        resolver,
        dispatcher,
    )

    dispatched = asyncio.run(processor.process(b"payload", "signature"))

    assert dispatched == 2
    assert dispatcher.events == [
        (InstagramConnectionId("connection-a"), first),
        (InstagramConnectionId("connection-b"), second),
    ]
    assert store.completed == {"event-a", "event-b"}
    assert resolver.calls == [
        InstagramAccountId("account-a"),
        InstagramAccountId("account-b"),
    ]


def test_processor_releases_idempotency_claim_when_dispatch_fails() -> None:
    event = build_event("event-a", "account-a")
    store = FakeInstagramWebhookIdempotencyStore()
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(True),
        FakeInstagramWebhookParser((event,)),
        store,
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account-a"): InstagramConnectionId("connection-a")}
        ),
        FakeInstagramWebhookEventDispatcher(fail_event_id="event-a"),
    )

    with pytest.raises(RuntimeError, match="dispatch failed"):
        asyncio.run(processor.process(b"payload", "signature"))

    assert store.release_calls == ["event-a"]
    assert store.completed == set()
    assert store.in_progress == set()
