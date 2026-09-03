"""Map Meta token DTOs to application grants."""

from datetime import timedelta

from instagram_auth.application import Clock, InstagramAuthorizationGrant
from instagram_auth.baseline import InstagramPermission
from instagram_auth.infrastructure.meta.dto import MetaInstagramTokenDto


class MetaAuthorizationGrantMapper:
    """Map validated provider token data to an application grant."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def map(self, dto: MetaInstagramTokenDto) -> InstagramAuthorizationGrant:
        expires_at = None
        if dto.expires_in is not None:
            expires_at = self._clock.now() + timedelta(seconds=dto.expires_in)
        granted_permissions = frozenset(
            permission
            for permission in InstagramPermission
            if permission.value in dto.permissions
        )
        return InstagramAuthorizationGrant(
            access_token=dto.access_token,
            expires_at=expires_at,
            granted_permissions=granted_permissions,
        )
