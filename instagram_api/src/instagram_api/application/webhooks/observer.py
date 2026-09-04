"""Default operational observer for Instagram webhooks."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookFailureDecision,
    InstagramWebhookOperationalObserver,
)
from instagram_api.domain import InstagramAccountId, InstagramConnectionId


class NullInstagramWebhookOperationalObserver(InstagramWebhookOperationalObserver):
    """No-op observer for hosts that do not configure metrics yet."""

    def signature_rejected(self) -> None:
        """Ignore signature rejection."""

    def duplicate_suppressed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
    ) -> None:
        del event_id, provider_account_id

    def event_dispatched(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId,
    ) -> None:
        del event_id, provider_account_id, connection_id

    def event_failed(
        self,
        *,
        event_id: str,
        provider_account_id: InstagramAccountId,
        connection_id: InstagramConnectionId | None,
        error_type: str,
        decision: InstagramWebhookFailureDecision,
    ) -> None:
        del event_id, provider_account_id, connection_id, error_type, decision
