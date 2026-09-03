"""Protect and persist one Instagram connection credential."""

from datetime import datetime

from instagram_auth.application.contracts import (
    InstagramAccessTokenProtector,
    InstagramCredentialRepository,
)
from instagram_auth.application.models import (
    InstagramAuthorizationGrant,
    InstagramProtectedCredential,
)
from instagram_auth.domain import InstagramConnectionId


class StoreInstagramConnectionCredential:
    """Protect raw provider credentials before they cross the persistence boundary."""

    def __init__(
        self,
        repository: InstagramCredentialRepository,
        token_protector: InstagramAccessTokenProtector,
    ) -> None:
        self._repository = repository
        self._token_protector = token_protector

    async def execute(
        self,
        *,
        connection_id: InstagramConnectionId,
        grant: InstagramAuthorizationGrant,
        last_validated_at: datetime | None = None,
    ) -> None:
        protected_access_token = self._token_protector.protect(grant.access_token)
        await self._repository.save(
            InstagramProtectedCredential(
                connection_id=connection_id,
                protected_access_token=protected_access_token,
                expires_at=grant.expires_at,
                last_validated_at=last_validated_at,
            )
        )
