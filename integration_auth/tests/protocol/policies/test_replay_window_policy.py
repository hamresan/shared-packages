"""Tests for ReplayWindowPolicy."""

import pytest

from integration_auth.protocol.policies.replay_window_policy import ReplayWindowPolicy


def test_rejects_non_positive_retention() -> None:
    with pytest.raises(ValueError, match="retention_seconds"):
        ReplayWindowPolicy(0)


def test_uses_retention_deadline_when_it_is_later() -> None:
    policy = ReplayWindowPolicy(600)

    assert (
        policy.nonce_expires_at(
            request_timestamp=1000,
            current_timestamp=1000,
            max_clock_skew_seconds=300,
        )
        == 1600
    )


def test_keeps_nonce_until_request_can_no_longer_be_accepted() -> None:
    policy = ReplayWindowPolicy(60)

    assert (
        policy.nonce_expires_at(
            request_timestamp=1000,
            current_timestamp=700,
            max_clock_skew_seconds=300,
        )
        == 1300
    )


@pytest.mark.parametrize(
    ("request_timestamp", "current_timestamp", "max_clock_skew_seconds"),
    [(-1, 0, 0), (0, -1, 0), (0, 0, -1)],
)
def test_rejects_negative_inputs(
    request_timestamp: int,
    current_timestamp: int,
    max_clock_skew_seconds: int,
) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ReplayWindowPolicy(1).nonce_expires_at(
            request_timestamp=request_timestamp,
            current_timestamp=current_timestamp,
            max_clock_skew_seconds=max_clock_skew_seconds,
        )
