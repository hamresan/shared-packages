"""Instagram webhook processing orchestration."""

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
from instagram_api.domain import InstagramConnectionId

from .errors import InstagramWebhookAuthenticationError


class InstagramWebhookProcessor:
    """Verifies, deduplicates, routes, dispatches, and records webhook outcomes."""

    def __init__(
        self,
        verifier: InstagramWebhookVerifier,
        parser: InstagramWebhookParser,
        idempotency_store: InstagramWebhookIdempotencyStore,
        connection_resolver: InstagramWebhookConnectionResolver,
        dispatcher: InstagramWebhookEventDispatcher,
        failure_handler: InstagramWebhookFailureHandler,
        observer: InstagramWebhookOperationalObserver,
    ) -> None:
        self._verifier = verifier
        self._parser = parser
        self._idempotency_store = idempotency_store
        self._connection_resolver = connection_resolver
        self._dispatcher = dispatcher
        self._failure_handler = failure_handler
        self._observer = observer

    async def process(self, payload: bytes, signature: str | None) -> int:
        """Process authentic non-duplicate events and return dispatch count."""

        if not self._verifier.verify(payload, signature):
            self._observer.signature_rejected()
            raise InstagramWebhookAuthenticationError("Instagram webhook signature is invalid.")

        dispatched = 0
        for event in self._parser.parse(payload):
            acquired = await self._idempotency_store.acquire(event.event_id)
            if not acquired:
                self._observer.duplicate_suppressed(
                    event_id=event.event_id,
                    provider_account_id=event.provider_account_id,
                )
                continue

            connection_id: InstagramConnectionId | None = None
            try:
                connection_id = await self._connection_resolver.resolve(event.provider_account_id)
                await self._dispatcher.dispatch(connection_id, event)
            except Exception as exc:
                decision = await self._failure_handler.handle(
                    event,
                    connection_id,
                    exc,
                )
                self._observer.event_failed(
                    event_id=event.event_id,
                    provider_account_id=event.provider_account_id,
                    connection_id=connection_id,
                    error_type=type(exc).__name__,
                    decision=decision,
                )
                if decision is InstagramWebhookFailureDecision.DISCARD:
                    await self._idempotency_store.complete(event.event_id)
                    continue

                await self._idempotency_store.release(event.event_id)
                raise

            await self._idempotency_store.complete(event.event_id)
            self._observer.event_dispatched(
                event_id=event.event_id,
                provider_account_id=event.provider_account_id,
                connection_id=connection_id,
            )
            dispatched += 1

        return dispatched
