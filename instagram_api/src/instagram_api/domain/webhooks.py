"""Normalized webhook models."""

from dataclasses import dataclass
from datetime import datetime

from .identifiers import InstagramAccountId
from .webhook_payloads import InstagramWebhookPayload


@dataclass(frozen=True, slots=True)
class InstagramWebhookEvent:
    """Provider-neutral webhook event envelope."""

    event_id: str
    event_type: str
    provider_account_id: InstagramAccountId
    occurred_at: datetime | None = None
    payload: InstagramWebhookPayload | None = None
