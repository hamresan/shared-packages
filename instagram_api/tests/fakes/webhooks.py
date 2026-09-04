"""Webhook contract fakes."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookConnectionResolver,
    InstagramWebhookEventDispatcher,
    InstagramWebhookFailureDecision,
    InstagramWebhookFailureHandler,
    InstagramWebhookIdempotencyStore,
    InstagramWebhookOperationalObserver,
    InstagramWebhookParser,
    InstagramWebhookVerifier,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramWebhookEvent,
)


class FakeInstagramWebhookVerifier(InstagramWebhookVerifier):
    """Fake verifier with configurable result."""

    def __init__(self, result: bool) -> None:
        self._result = result

    def verify(self, payload: bytes, signature: str | None) -> bool:
        del payload, signature
        return self._result


class FakeInstagramWebhookParser(InstagramWebhookParser):
    """Fake parser with preconfigured normalized events."""

    def __init__(self, events: tuple[InstagramWebhookEvent, ...]) -> None:
        self._events = events

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        del payload
        return self._events


class FakeInstagramWebhookIdempotencyStore(InstagramWebhookIdempotencyStore):
    """In-memory atomic claim fake for webhook processor tests."""

    def __init__(self) -> None:
        self.in_progress: set[str] = set()
        self.completed: set[str] = set()
        self.acquire_calls: list[str] = []
        self.complete_calls: list[str] = []
        self.release_calls: list[str] = []

    async def acquire(self, event_id: str) -> bool:
        self.acquire_calls.append(event_id)
        if event_id in self.in_progress or event_id in self.completed:
            return False
        self.in_progress.add(event_id)
        return True

    async def complete(self, event_id: str) -> None:
        self.complete_calls.append(event_id)
        self.in_progress.remove(event_id)
        self.completed.add(event_id)

    async def release(self, event_id: str) -> None:
        self.release_calls.append(event_id)
        self.in_progress.discard(event_id)


class FakeInstagramWebhookConnectionResolver(InstagramWebhookConnectionResolver):
    """Fake host resolver keyed by provider Instagram account ID."""

    def __init__(
        self,
        connections: dict[InstagramAccountId, InstagramConnectionId],
    ) -> None:
        self._connections = connections
        self.calls: list[InstagramAccountId] = []

    async def resolve(
        self,
        provider_account_id: InstagramAccountId,
    ) -> InstagramConnectionId:
        self.calls.append(provider_account_id)
        return self._connections[provider_account_id]


class FakeInstagramWebhookEventDispatcher(InstagramWebhookEventDispatcher):
    """Fake host dispatcher with optional failure."""

    def __init__(self, fail_event_id: str | None = None) -> None:
        self._fail_event_id = fail_event_id
        self.events: list[tuple[InstagramConnectionId, InstagramWebhookEvent]] = []

    async def dispatch(
        self,
        connection_id: InstagramConnectionId,
        event: InstagramWebhookEvent,
    ) -> None:
        if event.event_id == self._fail_event_id:
            raise RuntimeError("dispatch failed")
        self.events.append((connection_id, event))


class FakeInstagramWebhookFailureHandler(InstagramWebhookFailureHandler):
    """Fake poison-event handler with a configurable decision."""

    def __init__(
        self,
        decision: InstagramWebhookFailureDecision,
    ) -> None:
        self._decision = decision
        self.calls: list[
            tuple[InstagramWebhookEvent, InstagramConnectionId | None, Exception]
        ] = []

    async def handle(
        self,
        event: InstagramWebhookEvent,
        connection_id: InstagramConnectionId | None,
        error: Exception,
    ) -> InstagramWebhookFailureDecision:
        self.calls.append((event, connection_id, error))
        return self._decision


class FakeInstagramWebhookOperationalObserver(InstagramWebhookOperationalObserver):
    """Records structured webhook operational events."""

    def __init__(self) -> None:
        self.signature_rejections = 0
        self.duplicates: list[tuple[str, InstagramAccountId]] = []
        self.dispatched: list[
            tuple[str, InstagramAccountId, InstagramConnectionId]
        ] = []
        self.failures: list[
            tuple[
                str,
                InstagramAccountId,
                InstagramConnectionId | None,
                str,
                InstagramWebhookFailureDecision,
            ]
        ] = []

    def signature_rejected(self) -> None:
        self.signature_rejections += 1

    def duplicate_suppressed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
    ) -> None:
        self.duplicates.append((event_id, provider_account_id))

    def event_dispatched(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId,
    ) -> None:
        self.dispatched.append((event_id, provider_account_id, connection_id))

    def event_failed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId | None,
        error_type: str,
        decision: InstagramWebhookFailureDecision,
    ) -> None:
        self.failures.append(
            (
                event_id,
                provider_account_id,
                connection_id,
                error_type,
                decision,
            )
        )
