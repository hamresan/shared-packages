from identity.application.errors import ExternalIdentityAuthenticationError


class AccessTokenAuthenticationError(Exception):
    """Raised when access-token credentials are invalid or no longer acceptable."""


__all__ = [
    "AccessTokenAuthenticationError",
    "ExternalIdentityAuthenticationError",
    "SessionRefreshError",
    "SessionRefreshRejectedError",
]


class SessionRefreshError(Exception):
    """Raised when a session refresh operation fails through the public API."""


class SessionRefreshRejectedError(SessionRefreshError):
    """Raised when the supplied refresh credential is invalid or reused."""
