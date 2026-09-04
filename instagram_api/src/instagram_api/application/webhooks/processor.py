"""Instagram webhook processing orchestration."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookConnectionResolver,
    InstagramWebhookEventDispatcher,
    InstagramWebhookIdempotencyStore,
    InstagramWebhookParser,
    InstagramWebhookVerifier,
)

from .errors import InstagramWebhookAuthenticationError


class InstagramWebhookProcessor:
    """Verifies, parses, deduplicates, resolves, and dispatches webhook events."""

    def __init__(
        self,
        verifier: InstagramWebhookVerifier,
        parser: InstagramWebhookParser,
        idempotency_store: InstagramWebhookIdempotencyStore,
        connection_resolver: InstagramWebhookConnectionResolver,
        dispatcher: InstagramWebhookEventDispatcher,
    ) -> None:
        self._verifier = verifier
        self._parser = parser
        self._idempotency_store = idempotency_store
        self._connection_resolver = connection_resolver
        self._dispatcher = dispatcher

    async def process(self, payload: bytes, signature: str | None) -> int:
        """Process authentic non-duplicate events and return dispatch count."""

        if not self._verifier.verify(payload, signature):
            raise InstagramWebhookAuthenticationError("Instagram webhook signature is invalid.")

        dispatched = 0
        for event in self._parser.parse(payload):
            acquired = await self._idempotency_store.acquire(event.event_id)
            if not acquired:
                continue

            try:
                connection_id = await self._connection_resolver.resolve(event.provider_account_id)
                await self._dispatcher.dispatch(connection_id, event)
            except Exception:
                await self._idempotency_store.release(event.event_id)
                raise

            await self._idempotency_store.complete(event.event_id)
            dispatched += 1

        return dispatched
