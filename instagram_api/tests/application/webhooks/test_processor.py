"""Instagram webhook processor tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.contracts.webhooks import InstagramWebhookFailureDecision
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
    FakeInstagramWebhookFailureHandler,
    FakeInstagramWebhookIdempotencyStore,
    FakeInstagramWebhookOperationalObserver,
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
    observer = FakeInstagramWebhookOperationalObserver()
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(False),
        FakeInstagramWebhookParser((build_event("event", "account"),)),
        FakeInstagramWebhookIdempotencyStore(),
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account"): InstagramConnectionId("connection")}
        ),
        FakeInstagramWebhookEventDispatcher(),
        FakeInstagramWebhookFailureHandler(InstagramWebhookFailureDecision.RETRY),
        observer,
    )

    with pytest.raises(InstagramWebhookAuthenticationError):
        asyncio.run(processor.process(b"payload", "signature"))

    assert observer.signature_rejections == 1


def test_processor_routes_accounts_observes_success_and_suppresses_duplicate() -> None:
    first = build_event("event-a", "account-a")
    duplicate = build_event("event-a", "account-a")
    second = build_event("event-b", "account-b")
    store = FakeInstagramWebhookIdempotencyStore()
    observer = FakeInstagramWebhookOperationalObserver()
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
        FakeInstagramWebhookFailureHandler(InstagramWebhookFailureDecision.RETRY),
        observer,
    )

    dispatched = asyncio.run(processor.process(b"payload", "signature"))

    assert dispatched == 2
    assert dispatcher.events == [
        (InstagramConnectionId("connection-a"), first),
        (InstagramConnectionId("connection-b"), second),
    ]
    assert store.completed == {"event-a", "event-b"}
    assert observer.duplicates == [
        ("event-a", InstagramAccountId("account-a"))
    ]
    assert observer.dispatched == [
        (
            "event-a",
            InstagramAccountId("account-a"),
            InstagramConnectionId("connection-a"),
        ),
        (
            "event-b",
            InstagramAccountId("account-b"),
            InstagramConnectionId("connection-b"),
        ),
    ]


def test_processor_releases_retryable_failure_and_records_correlation() -> None:
    event = build_event("event-a", "account-a")
    store = FakeInstagramWebhookIdempotencyStore()
    observer = FakeInstagramWebhookOperationalObserver()
    failure_handler = FakeInstagramWebhookFailureHandler(
        InstagramWebhookFailureDecision.RETRY
    )
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(True),
        FakeInstagramWebhookParser((event,)),
        store,
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account-a"): InstagramConnectionId("connection-a")}
        ),
        FakeInstagramWebhookEventDispatcher(fail_event_id="event-a"),
        failure_handler,
        observer,
    )

    with pytest.raises(RuntimeError, match="dispatch failed"):
        asyncio.run(processor.process(b"payload", "signature"))

    assert store.release_calls == ["event-a"]
    assert store.completed == set()
    assert observer.failures == [
        (
            "event-a",
            InstagramAccountId("account-a"),
            InstagramConnectionId("connection-a"),
            "RuntimeError",
            InstagramWebhookFailureDecision.RETRY,
        )
    ]


def test_processor_completes_discarded_poison_event_without_raising() -> None:
    event = build_event("event-a", "account-a")
    store = FakeInstagramWebhookIdempotencyStore()
    observer = FakeInstagramWebhookOperationalObserver()
    processor = InstagramWebhookProcessor(
        FakeInstagramWebhookVerifier(True),
        FakeInstagramWebhookParser((event,)),
        store,
        FakeInstagramWebhookConnectionResolver(
            {InstagramAccountId("account-a"): InstagramConnectionId("connection-a")}
        ),
        FakeInstagramWebhookEventDispatcher(fail_event_id="event-a"),
        FakeInstagramWebhookFailureHandler(InstagramWebhookFailureDecision.DISCARD),
        observer,
    )

    dispatched = asyncio.run(processor.process(b"payload", "signature"))

    assert dispatched == 0
    assert store.completed == {"event-a"}
    assert store.release_calls == []
    assert observer.failures[0][-1] is InstagramWebhookFailureDecision.DISCARD
