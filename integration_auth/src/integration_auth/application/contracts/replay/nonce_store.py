"""Atomic nonce consumption contract for replay protection."""

from typing import Protocol

from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class NonceStore(Protocol):
    """Atomically consume a nonce for one integration client."""

    async def consume_once(
        self,
        *,
        client_id: IntegrationClientId,
        nonce: str,
        expires_at_timestamp: int,
    ) -> bool:
        """Return true only for the first atomic consumption of a client nonce."""
        ...
