"""Host boundaries for Instagram webhook routing."""

from typing import Protocol

from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramWebhookEvent,
)


class InstagramWebhookConnectionResolver(Protocol):
    """Resolves a provider Instagram account to a host connection."""

    async def resolve(
        self,
        provider_account_id: InstagramAccountId,
    ) -> InstagramConnectionId:
        """Return the host connection that owns the provider account."""
        ...


class InstagramWebhookEventDispatcher(Protocol):
    """Dispatches normalized webhook events to host-owned logic."""

    async def dispatch(
        self,
        connection_id: InstagramConnectionId,
        event: InstagramWebhookEvent,
    ) -> None:
        """Dispatch a normalized event through its resolved connection."""
        ...
