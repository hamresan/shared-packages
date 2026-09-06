"""Deterministic event ID creation for Meta webhook entries."""

import hashlib
import json
from collections.abc import Mapping


class MetaInstagramWebhookEventIdFactory:
    """Creates stable IDs for webhook items lacking provider event IDs."""

    def create(
        self,
        *,
        provider_account_id: str,
        event_type: str,
        occurred_at_seconds: int | None,
        item: Mapping[str, object],
    ) -> str:
        """Return a deterministic SHA-256 event identifier."""

        message = item.get("message")
        if event_type == "messaging" and isinstance(message, Mapping):
            provider_message_id = message.get("mid")
            if isinstance(provider_message_id, str) and provider_message_id:
                canonical = json.dumps(
                    {
                        "provider_account_id": provider_account_id,
                        "event_type": event_type,
                        "provider_message_id": provider_message_id,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                )
                return hashlib.sha256(canonical.encode()).hexdigest()

        canonical = json.dumps(
            {
                "provider_account_id": provider_account_id,
                "event_type": event_type,
                "occurred_at_seconds": occurred_at_seconds,
                "item": item,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()
