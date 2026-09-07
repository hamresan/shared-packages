"""Access-token refresh boundary for Instagram authorization."""

from typing import Protocol

from instagram_auth.application.models import InstagramAuthorizationGrant


class InstagramAccessTokenRefresher(Protocol):
    """Refresh one still-valid Instagram access token through the provider."""

    async def refresh_access_token(self, *, access_token: str) -> InstagramAuthorizationGrant:
        """Return refreshed token material and lifecycle metadata."""
        ...
