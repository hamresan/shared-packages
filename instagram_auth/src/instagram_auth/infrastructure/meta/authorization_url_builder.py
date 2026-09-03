"""Meta Instagram Login authorization URL builder."""

from collections.abc import Collection
from urllib.parse import urlencode

from instagram_auth.application.contracts import InstagramAuthorizationUrlBuilder
from instagram_auth.baseline import InstagramPermission


class MetaInstagramAuthorizationUrlBuilder(InstagramAuthorizationUrlBuilder):
    """Build Instagram Login OAuth authorization URLs."""

    DEFAULT_AUTHORIZATION_ENDPOINT = "https://www.instagram.com/oauth/authorize"

    def __init__(
        self,
        *,
        client_id: str,
        authorization_endpoint: str = DEFAULT_AUTHORIZATION_ENDPOINT,
    ) -> None:
        if not client_id:
            raise ValueError("client_id is required")
        if not authorization_endpoint:
            raise ValueError("authorization_endpoint is required")
        self._client_id = client_id
        self._authorization_endpoint = authorization_endpoint

    def build(
        self,
        *,
        redirect_uri: str,
        state: str,
        permissions: Collection[InstagramPermission],
    ) -> str:
        """Build a provider URL using explicit least-privilege scopes."""
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": ",".join(sorted(permission.value for permission in permissions)),
                "state": state,
            }
        )
        return f"{self._authorization_endpoint}?{query}"
