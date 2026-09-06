"""Maps generic Meta webhook items to normalized webhook events."""

from collections.abc import Mapping
from datetime import UTC, datetime

from instagram_api.domain import (
    InstagramAccountId,
    InstagramWebhookEvent,
    InstagramWebhookPayload,
)

from .event_id import MetaInstagramWebhookEventIdFactory
from .timestamp_normalizer import normalize_meta_webhook_epoch_seconds


class MetaInstagramWebhookEventMapper:
    """Maps provider envelope items to generic normalized events."""

    def __init__(self, event_id_factory: MetaInstagramWebhookEventIdFactory) -> None:
        self._event_id_factory = event_id_factory

    def to_domain(
        self,
        *,
        account_id: str,
        event_type: str,
        occurred_at_seconds: int | None,
        item: Mapping[str, object],
        payload: InstagramWebhookPayload | None = None,
    ) -> InstagramWebhookEvent:
        """Create one normalized generic webhook event."""

        occurred_at = (
            datetime.fromtimestamp(
                normalize_meta_webhook_epoch_seconds(occurred_at_seconds),
                tz=UTC,
            )
            if occurred_at_seconds is not None
            else None
        )
        return InstagramWebhookEvent(
            event_id=self._event_id_factory.create(
                provider_account_id=account_id,
                event_type=event_type,
                occurred_at_seconds=occurred_at_seconds,
                item=item,
            ),
            event_type=event_type,
            provider_account_id=InstagramAccountId(account_id),
            occurred_at=occurred_at,
            payload=payload,
        )
