"""Build protected credential models for persistence."""

from instagram_auth.application.contracts import Clock, InstagramAccessTokenProtector
from instagram_auth.application.models import (
    InstagramAuthorizationGrant,
    InstagramProtectedCredential,
)
from instagram_auth.domain import InstagramConnectionId


class InstagramProtectedCredentialFactory:
    """Protect provider credentials and build persistence-safe application models."""

    def __init__(
        self,
        token_protector: InstagramAccessTokenProtector,
        clock: Clock,
    ) -> None:
        self._token_protector = token_protector
        self._clock = clock

    def build(
        self,
        *,
        connection_id: InstagramConnectionId,
        grant: InstagramAuthorizationGrant,
    ) -> InstagramProtectedCredential:
        return InstagramProtectedCredential(
            connection_id=connection_id,
            protected_access_token=self._token_protector.protect(grant.access_token),
            expires_at=grant.expires_at,
            last_validated_at=self._clock.now(),
        )
