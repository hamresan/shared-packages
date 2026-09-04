"""Operational resilience contracts for Instagram webhooks."""

from enum import StrEnum
from typing import Protocol

from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramWebhookEvent,
)


class InstagramWebhookFailureDecision(StrEnum):
    """Host decision for a failed webhook event."""

    RETRY = "retry"
    DISCARD = "discard"


class InstagramWebhookFailureHandler(Protocol):
    """Decides how a failed webhook event should be treated."""

    async def handle(
        self,
        event: InstagramWebhookEvent,
        connection_id: InstagramConnectionId | None,
        error: Exception,
    ) -> InstagramWebhookFailureDecision:
        """Return whether the delivery should retry or be discarded."""
        ...


class InstagramWebhookOperationalObserver(Protocol):
    """Receives structured webhook operational events without secrets."""

    def signature_rejected(self) -> None:
        """Record a rejected webhook signature."""
        ...

    def duplicate_suppressed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
    ) -> None:
        """Record a repeated provider delivery."""
        ...

    def event_dispatched(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId,
    ) -> None:
        """Record a successfully dispatched event."""
        ...

    def event_failed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId | None,
        error_type: str,
        decision: InstagramWebhookFailureDecision,
    ) -> None:
        """Record a failed event without request credentials or raw payloads."""
        ...
