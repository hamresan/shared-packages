"""Map domain entities to HTTP response schemas."""

from instagram_auth.domain import InstagramConnection

from .schemas import InstagramConnectionResponse


class InstagramConnectionResponseMapper:
    """Convert secret-free connection entities to transport responses."""

    def map(self, connection: InstagramConnection) -> InstagramConnectionResponse:
        return InstagramConnectionResponse(
            id=str(connection.id.value),
            instagram_account_id=connection.instagram_account_id,
            username=connection.username,
            account_type=connection.account_type,
            permissions=sorted(connection.permissions, key=lambda permission: permission.value),
            status=connection.status,
            connected_at=connection.connected_at,
            credential_expires_at=connection.credential_expires_at,
            revoked_at=connection.revoked_at,
            last_validated_at=connection.last_validated_at,
            version=connection.version,
        )
