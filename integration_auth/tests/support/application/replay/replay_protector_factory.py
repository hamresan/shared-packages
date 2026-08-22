"""Test factory for ReplayProtector."""

from integration_auth.application.services.replay.replay_protector import ReplayProtector
from integration_auth.protocol.policies.replay_window_policy import ReplayWindowPolicy
from integration_auth.protocol.policies.timestamp_tolerance_policy import TimestampTolerancePolicy
from tests.support.application.replay.atomic_nonce_store_fake import AtomicNonceStoreFake


def build_replay_protector(
    nonce_store: AtomicNonceStoreFake,
    *,
    max_clock_skew_seconds: int = 300,
    retention_seconds: int = 600,
) -> ReplayProtector:
    """Build a ReplayProtector with explicit test policies."""
    return ReplayProtector(
        nonce_store=nonce_store,
        timestamp_policy=TimestampTolerancePolicy(max_clock_skew_seconds),
        replay_window_policy=ReplayWindowPolicy(retention_seconds),
    )
