from identity.application.errors import ExternalIdentityAuthenticationError


class AccessTokenAuthenticationError(Exception):
    """Raised when access-token credentials are invalid or no longer acceptable."""


__all__ = ["AccessTokenAuthenticationError", "ExternalIdentityAuthenticationError"]
