import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta

from identity.application.contracts.rate_limiting import (
    RateLimitDecision,
    RateLimiter,
    RateLimitRule,
)


@dataclass(slots=True)
class _RateLimitBucket:
    window_started_at: datetime
    count: int


class InMemoryRateLimiter(RateLimiter):
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], _RateLimitBucket] = {}
        self._lock = asyncio.Lock()

    async def consume(
        self,
        *,
        scope: str,
        key: str,
        rule: RateLimitRule,
        now: datetime,
    ) -> RateLimitDecision:
        bucket_key = (scope, key)
        async with self._lock:
            bucket = self._buckets.get(bucket_key)
            if bucket is None or now - bucket.window_started_at >= rule.window:
                self._buckets[bucket_key] = _RateLimitBucket(window_started_at=now, count=1)
                return RateLimitDecision(allowed=True)

            if bucket.count >= rule.limit:
                elapsed = now - bucket.window_started_at
                return RateLimitDecision(
                    allowed=False,
                    retry_after=max(timedelta(seconds=1), rule.window - elapsed),
                )

            bucket.count += 1
            return RateLimitDecision(allowed=True)
