"""Map SQLAlchemy records to package-owned domain/application models."""

from uuid import UUID

from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.baseline import InstagramAccountType, InstagramConnectionState, InstagramPermission
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from instagram_auth.infrastructure.persistence.models import InstagramConnectionRecord


class InstagramConnectionRecordMapper:
    """Map persistence records without leaking SQLAlchemy into domain/application code."""

    def to_record(self, connection: InstagramConnection) -> InstagramConnectionRecord:
        return InstagramConnectionRecord(
            id=str(connection.id.value),
            owner_user_id=connection.owner_user_id,
            instagram_account_id=connection.instagram_account_id,
            username=connection.username,
            account_type=connection.account_type.value,
            permissions=sorted(permission.value for permission in connection.permissions),
            status=connection.status.value,
            connected_at=connection.connected_at,
            credential_expires_at=connection.credential_expires_at,
            revoked_at=connection.revoked_at,
            last_validated_at=connection.last_validated_at,
            version=connection.version,
        )

    def to_domain(self, record: InstagramConnectionRecord) -> InstagramConnection:
        return InstagramConnection(
            id=InstagramConnectionId(UUID(record.id)),
            owner_user_id=record.owner_user_id,
            instagram_account_id=record.instagram_account_id,
            username=record.username,
            account_type=InstagramAccountType(record.account_type),
            permissions=frozenset(InstagramPermission(value) for value in record.permissions),
            status=InstagramConnectionState(record.status),
            connected_at=record.connected_at,
            credential_expires_at=record.credential_expires_at,
            revoked_at=record.revoked_at,
            last_validated_at=record.last_validated_at,
            version=record.version,
        )


class InstagramCredentialRecordMapper:
    """Map protected credential fields without exposing the ORM record."""

    def to_application(
        self,
        record: InstagramConnectionRecord,
    ) -> InstagramProtectedCredential | None:
        if record.protected_access_token is None:
            return None
        return InstagramProtectedCredential(
            connection_id=InstagramConnectionId(UUID(record.id)),
            protected_access_token=record.protected_access_token,
            expires_at=record.credential_expires_at,
            revoked_at=record.revoked_at,
            last_validated_at=record.last_validated_at,
        )
