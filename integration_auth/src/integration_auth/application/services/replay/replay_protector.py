"""Replay-protection application service."""

from integration_auth.application.contracts.replay.nonce_store import NonceStore
from integration_auth.application.errors.replay import (
    ReplayDetectedError,
    TimestampOutsideToleranceError,
)
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.protocol.policies.replay_window_policy import ReplayWindowPolicy
from integration_auth.protocol.policies.timestamp_tolerance_policy import TimestampTolerancePolicy
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class ReplayProtector:
    """Reject stale requests and atomically consume integration nonces."""

    def __init__(
        self,
        *,
        nonce_store: NonceStore,
        timestamp_policy: TimestampTolerancePolicy,
        replay_window_policy: ReplayWindowPolicy,
    ) -> None:
        self._nonce_store = nonce_store
        self._timestamp_policy = timestamp_policy
        self._replay_window_policy = replay_window_policy

    async def protect(
        self,
        *,
        client_id: IntegrationClientId,
        request: CanonicalRequest,
        current_timestamp: int,
    ) -> None:
        """Raise when timestamp or nonce makes the request unsafe to accept."""
        if not self._timestamp_policy.allows(
            request_timestamp=request.timestamp,
            current_timestamp=current_timestamp,
        ):
            raise TimestampOutsideToleranceError(
                "request timestamp is outside the allowed clock skew"
            )

        expires_at_timestamp = self._replay_window_policy.nonce_expires_at(
            request_timestamp=request.timestamp,
            current_timestamp=current_timestamp,
            max_clock_skew_seconds=self._timestamp_policy.max_clock_skew_seconds,
        )
        consumed = await self._nonce_store.consume_once(
            client_id=client_id,
            nonce=request.nonce,
            expires_at_timestamp=expires_at_timestamp,
        )
        if not consumed:
            raise ReplayDetectedError("request nonce has already been consumed")
