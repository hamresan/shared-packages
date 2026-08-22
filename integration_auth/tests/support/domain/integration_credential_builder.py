"""Test builder for IntegrationCredential."""

from datetime import UTC, datetime

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class IntegrationCredentialBuilder:
    """Build valid credential snapshots with focused test overrides."""

    def __init__(self) -> None:
        self.credential_id = IntegrationCredentialId("credential-123")
        self.client_id = IntegrationClientId("client-123")
        self.direction = CredentialDirection.INBOUND
        self.status = CredentialStatus.ACTIVE
        self.issued_at = datetime(2026, 8, 22, 10, 0, tzinfo=UTC)
        self.expires_at: datetime | None = None
        self.revoked_at: datetime | None = None

    def build(self) -> IntegrationCredential:
        """Build an IntegrationCredential from the current values."""
        return IntegrationCredential(
            credential_id=self.credential_id,
            client_id=self.client_id,
            direction=self.direction,
            status=self.status,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
        )
