from datetime import datetime
from uuid import UUID

from identity.application.contracts.rate_limiting import RateLimiter, RateLimitRule
from identity.application.errors import IdentityRateLimitExceededError


class OtpRateLimitPolicy:
    def __init__(
        self,
        *,
        rate_limiter: RateLimiter,
        request_burst_rule: RateLimitRule,
        request_daily_rule: RateLimitRule,
        verify_rule: RateLimitRule,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._request_burst_rule = request_burst_rule
        self._request_daily_rule = request_daily_rule
        self._verify_rule = verify_rule

    async def ensure_request_allowed(self, destination: str, now: datetime) -> None:
        burst = await self._rate_limiter.consume(
            scope="otp_request_burst",
            key=destination,
            rule=self._request_burst_rule,
            now=now,
        )
        if not burst.allowed:
            raise IdentityRateLimitExceededError.from_retry_after(burst.retry_after)

        daily = await self._rate_limiter.consume(
            scope="otp_request_daily",
            key=destination,
            rule=self._request_daily_rule,
            now=now,
        )
        if not daily.allowed:
            raise IdentityRateLimitExceededError.from_retry_after(daily.retry_after)

    async def ensure_verification_allowed(self, challenge_id: UUID, now: datetime) -> None:
        decision = await self._rate_limiter.consume(
            scope="otp_verify",
            key=str(challenge_id),
            rule=self._verify_rule,
            now=now,
        )
        if not decision.allowed:
            raise IdentityRateLimitExceededError.from_retry_after(decision.retry_after)
