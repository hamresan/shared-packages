from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from identity.application.contracts.rate_limiting import RateLimitRule
from identity.application.errors import IdentityRateLimitExceededError
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.infrastructure.security.in_memory_rate_limiter import InMemoryRateLimiter


def build_policy(
    *,
    destination_burst_limit: int = 1,
    requester_burst_limit: int = 2,
) -> OtpRateLimitPolicy:
    return OtpRateLimitPolicy(
        rate_limiter=InMemoryRateLimiter(),
        request_burst_rule=RateLimitRule(
            limit=destination_burst_limit,
            window=timedelta(minutes=1),
        ),
        request_daily_rule=RateLimitRule(limit=10, window=timedelta(days=1)),
        requester_burst_rule=RateLimitRule(
            limit=requester_burst_limit,
            window=timedelta(minutes=15),
        ),
        verify_rule=RateLimitRule(limit=1, window=timedelta(minutes=1)),
    )


@pytest.mark.asyncio
async def test_request_policy_limits_same_destination() -> None:
    policy = build_policy()
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)

    await policy.ensure_request_allowed("user@example.com", None, now)

    with pytest.raises(IdentityRateLimitExceededError) as error:
        await policy.ensure_request_allowed("user@example.com", None, now)

    assert error.value.retry_after_seconds == 60


@pytest.mark.asyncio
async def test_requester_limit_applies_across_different_destinations() -> None:
    policy = build_policy(destination_burst_limit=10, requester_burst_limit=2)
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)
    requester_key = "203.0.113.10"

    await policy.ensure_request_allowed("first@example.com", requester_key, now)
    await policy.ensure_request_allowed("second@example.com", requester_key, now)

    with pytest.raises(IdentityRateLimitExceededError):
        await policy.ensure_request_allowed("third@example.com", requester_key, now)


@pytest.mark.asyncio
async def test_verification_policy_limits_same_challenge() -> None:
    policy = build_policy()
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)
    challenge_id = uuid4()

    await policy.ensure_verification_allowed(challenge_id, now)

    with pytest.raises(IdentityRateLimitExceededError):
        await policy.ensure_verification_allowed(challenge_id, now)
