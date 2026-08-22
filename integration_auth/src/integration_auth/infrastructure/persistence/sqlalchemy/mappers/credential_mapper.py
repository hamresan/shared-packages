"""Map integration credentials between domain and SQLAlchemy records."""

from datetime import UTC, datetime

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from integration_auth.infrastructure.persistence.sqlalchemy.models.credential_record import (
    IntegrationCredentialRecord,
)


class IntegrationCredentialRecordMapper:
    """Convert credential persistence data without exposing protected material to the domain."""

    def to_record(
        self,
        credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> IntegrationCredentialRecord:
        record = IntegrationCredentialRecord(
            credential_id=credential.credential_id.value,
            client_id=credential.client_id.value,
            protected_secret=protected_secret.value,
        )
        self.apply_metadata(record, credential)
        return record

    def apply_metadata(
        self,
        record: IntegrationCredentialRecord,
        credential: IntegrationCredential,
    ) -> None:
        """Apply domain-owned credential metadata while preserving protected material."""
        record.direction = credential.direction.value
        record.status = credential.status.value
        record.issued_at = credential.issued_at
        record.expires_at = credential.expires_at
        record.revoked_at = credential.revoked_at

    def to_domain(self, record: IntegrationCredentialRecord) -> IntegrationCredential:
        return IntegrationCredential(
            credential_id=IntegrationCredentialId(record.credential_id),
            client_id=IntegrationClientId(record.client_id),
            direction=CredentialDirection(record.direction),
            status=CredentialStatus(record.status),
            issued_at=self._aware(record.issued_at),
            expires_at=self._optional_aware(record.expires_at),
            revoked_at=self._optional_aware(record.revoked_at),
        )

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @classmethod
    def _optional_aware(cls, value: datetime | None) -> datetime | None:
        return None if value is None else cls._aware(value)
