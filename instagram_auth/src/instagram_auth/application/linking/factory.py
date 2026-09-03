"""Build new or refreshed Instagram connection entities."""

from dataclasses import replace

from instagram_auth.application.contracts import Clock
from instagram_auth.application.contracts.connection_id_generator import (
    InstagramConnectionIdGenerator,
)
from instagram_auth.application.models import InstagramAuthorizationGrant
from instagram_auth.baseline import InstagramConnectionState
from instagram_auth.domain import InstagramConnection, InstagramExternalIdentity


class InstagramConnectionFactory:
    """Create or refresh a connection without persistence concerns."""

    def __init__(
        self,
        clock: Clock,
        id_generator: InstagramConnectionIdGenerator,
    ) -> None:
        self._clock = clock
        self._id_generator = id_generator

    def build(
        self,
        *,
        owner_user_id: str,
        identity: InstagramExternalIdentity,
        grant: InstagramAuthorizationGrant,
        existing: InstagramConnection | None,
    ) -> InstagramConnection:
        now = self._clock.now()
        if existing is not None:
            return replace(
                existing,
                username=identity.username,
                account_type=identity.account_type,
                permissions=grant.granted_permissions,
                status=InstagramConnectionState.CONNECTED,
                credential_expires_at=grant.expires_at,
                revoked_at=None,
                last_validated_at=now,
            )
        return InstagramConnection(
            id=self._id_generator.generate(),
            owner_user_id=owner_user_id,
            instagram_account_id=identity.provider_user_id,
            username=identity.username,
            account_type=identity.account_type,
            permissions=grant.granted_permissions,
            status=InstagramConnectionState.CONNECTED,
            connected_at=now,
            credential_expires_at=grant.expires_at,
            last_validated_at=now,
        )
