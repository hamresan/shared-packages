"""Access-token protection boundary."""

from typing import Protocol


class InstagramAccessTokenProtector(Protocol):
    """Protect and recover provider access tokens without exposing implementation details."""

    def protect(self, access_token: str) -> str:
        """Protect a raw access token for persistence."""
        ...

    def unprotect(self, protected_access_token: str) -> str:
        """Recover a raw access token for provider use."""
        ...
