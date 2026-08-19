from fastapi import HTTPException, status

from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
    IdentityRateLimitExceededError,
    InactiveUserError,
    InvalidOtpError,
    InvalidRefreshTokenError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
    OtpResendNotAvailableError,
    RegistrationNameRequiredError,
    UnsupportedOtpPurposeError,
)


class IdentityHttpErrorMapper:
    def to_http_exception(self, error: Exception) -> HTTPException:
        if isinstance(error, IdentityRateLimitExceededError):
            return HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                str(error),
                headers={"Retry-After": str(error.retry_after_seconds)},
            )
        if isinstance(error, OtpResendNotAvailableError):
            return HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(error))
        if isinstance(error, (IdentityAlreadyRegisteredError, IdentityNotRegisteredError)):
            return HTTPException(status.HTTP_409_CONFLICT, str(error))
        if isinstance(error, InactiveUserError):
            return HTTPException(status.HTTP_403_FORBIDDEN, str(error))
        if isinstance(error, (RegistrationNameRequiredError, UnsupportedOtpPurposeError)):
            return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))
        if isinstance(error, OtpChallengeNotFoundError):
            return HTTPException(status.HTTP_404_NOT_FOUND, str(error))
        if isinstance(error, (InvalidOtpError, InvalidRefreshTokenError)):
            return HTTPException(status.HTTP_401_UNAUTHORIZED, str(error))
        if isinstance(error, (OtpExpiredError, OtpAttemptsExceededError)):
            return HTTPException(status.HTTP_410_GONE, str(error))
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Identity operation failed")
