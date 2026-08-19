from datetime import timedelta


class IdentityError(Exception):
    """Base application error for identity flows."""


class OtpResendNotAvailableError(IdentityError):
    pass


class IdentityRateLimitExceededError(IdentityError):
    def __init__(self, message: str, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds

    @classmethod
    def from_retry_after(cls, retry_after: timedelta | None) -> "IdentityRateLimitExceededError":
        seconds = 1 if retry_after is None else max(1, int(retry_after.total_seconds()))
        return cls("Identity rate limit exceeded", seconds)


class OtpChallengeNotFoundError(IdentityError):
    pass


class InvalidOtpError(IdentityError):
    pass


class OtpExpiredError(IdentityError):
    pass


class OtpAttemptsExceededError(IdentityError):
    pass


class RegistrationNameRequiredError(IdentityError):
    pass


class IdentityAlreadyRegisteredError(IdentityError):
    pass


class IdentityNotRegisteredError(IdentityError):
    pass


class UnsupportedOtpPurposeError(IdentityError):
    pass


class InactiveUserError(IdentityError):
    pass


class InvalidRefreshTokenError(IdentityError):
    pass


class RefreshTokenReuseError(InvalidRefreshTokenError):
    pass
