from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from identity.application.contracts.rate_limiting import RateLimitRule
from identity.application.errors import IdentityRateLimitExceededError
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.infrastructure.security.in_memory_rate_limiter import InMemoryRateLimiter


def build_policy() -> OtpRateLimitPolicy:
    return OtpRateLimitPolicy(
        rate_limiter=InMemoryRateLimiter(),
        request_burst_rule=RateLimitRule(limit=1, window=timedelta(minutes=1)),
        request_daily_rule=RateLimitRule(limit=10, window=timedelta(days=1)),
        verify_rule=RateLimitRule(limit=1, window=timedelta(minutes=1)),
    )


@pytest.mark.asyncio
async def test_request_policy_limits_same_destination() -> None:
    policy = build_policy()
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)

    await policy.ensure_request_allowed("user@example.com", now)

    with pytest.raises(IdentityRateLimitExceededError) as error:
        await policy.ensure_request_allowed("user@example.com", now)

    assert error.value.retry_after_seconds == 60


@pytest.mark.asyncio
async def test_verification_policy_limits_same_challenge() -> None:
    policy = build_policy()
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)
    challenge_id = uuid4()

    await policy.ensure_verification_allowed(challenge_id, now)

    with pytest.raises(IdentityRateLimitExceededError):
        await policy.ensure_verification_allowed(challenge_id, now)
