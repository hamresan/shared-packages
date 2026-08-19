from datetime import UTC, datetime, timedelta

import pytest

from identity.application.contracts.rate_limiting import RateLimitRule
from identity.infrastructure.security.in_memory_rate_limiter import InMemoryRateLimiter


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_blocks_and_resets_fixed_window() -> None:
    limiter = InMemoryRateLimiter()
    rule = RateLimitRule(limit=2, window=timedelta(minutes=1))
    now = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)

    first = await limiter.consume(scope="otp", key="user@example.com", rule=rule, now=now)
    second = await limiter.consume(scope="otp", key="user@example.com", rule=rule, now=now)
    blocked = await limiter.consume(scope="otp", key="user@example.com", rule=rule, now=now)
    reset = await limiter.consume(
        scope="otp",
        key="user@example.com",
        rule=rule,
        now=now + timedelta(minutes=1),
    )

    assert first.allowed is True
    assert second.allowed is True
    assert blocked.allowed is False
    assert blocked.retry_after == timedelta(minutes=1)
    assert reset.allowed is True
