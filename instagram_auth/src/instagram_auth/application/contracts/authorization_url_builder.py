"""Provider authorization URL construction boundary."""

from collections.abc import Collection
from typing import Protocol

from instagram_auth.baseline import InstagramPermission


class InstagramAuthorizationUrlBuilder(Protocol):
    """Build the provider authorization URL without exposing provider details upstream."""

    def build(
        self,
        *,
        redirect_uri: str,
        state: str,
        permissions: Collection[InstagramPermission],
    ) -> str:
        """Build an authorization URL for the supplied callback and permissions."""
        ...
