"""Credential builder specialized for rotation policy tests."""

from datetime import UTC, datetime, timedelta

from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder


class RotationCredentialBuilder(IntegrationCredentialBuilder):
    """Build credentials around one fixed rotation timestamp."""

    def __init__(
        self,
        *,
        current_timestamp: int,
        client_id: IntegrationClientId,
    ) -> None:
        super().__init__()
        self.client_id = client_id
        self.issued_at = datetime.fromtimestamp(current_timestamp, tz=UTC) - timedelta(minutes=1)

    def with_credential_id(self, credential_id: str) -> "RotationCredentialBuilder":
        self.credential_id = IntegrationCredentialId(credential_id)
        return self

    def with_direction(self, direction: CredentialDirection) -> "RotationCredentialBuilder":
        self.direction = direction
        return self

    def revoked(self, current_timestamp: int) -> "RotationCredentialBuilder":
        self.status = CredentialStatus.REVOKED
        self.revoked_at = datetime.fromtimestamp(current_timestamp, tz=UTC) - timedelta(seconds=1)
        return self
