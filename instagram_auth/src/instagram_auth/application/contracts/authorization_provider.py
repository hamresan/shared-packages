"""Provider-facing authorization contract."""

from typing import Protocol

from instagram_auth.application.models import InstagramAuthorizationGrant
from instagram_auth.domain import InstagramExternalIdentity


class InstagramAuthorizationProvider(Protocol):
    """Boundary implemented by provider-specific Instagram authorization adapters."""

    async def exchange_authorization_code(
        self,
        *,
        authorization_code: str,
        redirect_uri: str,
    ) -> InstagramAuthorizationGrant:
        """Exchange an authorization code for a transient provider grant."""
        ...

    async def resolve_external_identity(
        self,
        *,
        access_token: str,
    ) -> InstagramExternalIdentity:
        """Resolve the authenticated professional Instagram identity."""
        ...
