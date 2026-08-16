class IdentityError(Exception):
    """Base application error for identity flows."""


class OtpResendNotAvailableError(IdentityError):
    pass


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


class InvalidRefreshTokenError(IdentityError):
    pass
