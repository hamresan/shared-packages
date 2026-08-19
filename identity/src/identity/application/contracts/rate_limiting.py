from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RateLimitRule:
    limit: int
    window: timedelta


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    retry_after: timedelta | None = None


class RateLimiter(Protocol):
    async def consume(
        self,
        *,
        scope: str,
        key: str,
        rule: RateLimitRule,
        now: datetime,
    ) -> RateLimitDecision: ...
