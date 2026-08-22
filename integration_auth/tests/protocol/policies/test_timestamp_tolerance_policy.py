import pytest

from integration_auth.protocol.policies.timestamp_tolerance_policy import TimestampTolerancePolicy


def test_allows_timestamp_on_both_clock_skew_boundaries() -> None:
    policy = TimestampTolerancePolicy(max_clock_skew_seconds=300)

    assert policy.allows(request_timestamp=700, current_timestamp=1000)
    assert policy.allows(request_timestamp=1300, current_timestamp=1000)


def test_rejects_timestamp_outside_clock_skew() -> None:
    policy = TimestampTolerancePolicy(max_clock_skew_seconds=300)

    assert not policy.allows(request_timestamp=699, current_timestamp=1000)
    assert not policy.allows(request_timestamp=1301, current_timestamp=1000)


def test_rejects_negative_timestamps() -> None:
    policy = TimestampTolerancePolicy(max_clock_skew_seconds=300)

    assert not policy.allows(request_timestamp=-1, current_timestamp=1000)
    assert not policy.allows(request_timestamp=1000, current_timestamp=-1)


def test_rejects_negative_clock_skew_configuration() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        TimestampTolerancePolicy(max_clock_skew_seconds=-1)


def test_exposes_configured_clock_skew() -> None:
    assert TimestampTolerancePolicy(300).max_clock_skew_seconds == 300
