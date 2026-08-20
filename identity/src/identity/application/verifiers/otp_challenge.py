from datetime import datetime

from identity.application.contracts.security import SecretHasher
from identity.application.errors import (
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
)
from identity.domain import OtpChallenge


class OtpChallengeVerifier:
    def __init__(self, hasher: SecretHasher) -> None:
        self._hasher = hasher

    def verify(
        self,
        *,
        challenge: OtpChallenge | None,
        code: str,
        now: datetime,
    ) -> OtpChallenge:
        if challenge is None or challenge.consumed_at is not None:
            raise OtpChallengeNotFoundError("OTP challenge was not found")
        if challenge.expires_at <= now:
            raise OtpExpiredError("OTP challenge has expired")
        if challenge.attempts_count >= challenge.max_attempts:
            raise OtpAttemptsExceededError("OTP attempts exceeded")
        if not self._hasher.verify(code, challenge.code_hash):
            raise InvalidOtpError("OTP code is invalid")
        return challenge
