"""Atomic in-memory nonce store fake for replay tests."""

import asyncio

from integration_auth.application.contracts.replay.nonce_store import NonceStore
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class AtomicNonceStoreFake(NonceStore):
    """Test fake that preserves atomic consume-once semantics."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._consumed: set[tuple[IntegrationClientId, str]] = set()
        self.calls: list[tuple[IntegrationClientId, str, int]] = []

    async def consume_once(
        self,
        *,
        client_id: IntegrationClientId,
        nonce: str,
        expires_at_timestamp: int,
    ) -> bool:
        async with self._lock:
            self.calls.append((client_id, nonce, expires_at_timestamp))
            key = (client_id, nonce)
            if key in self._consumed:
                return False

            self._consumed.add(key)
            await asyncio.sleep(0)
            return True
