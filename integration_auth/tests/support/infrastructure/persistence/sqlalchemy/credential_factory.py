"""Credential factory for SQLAlchemy persistence tests."""

from datetime import UTC, datetime

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)

PERSISTENCE_TEST_ISSUED_AT = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
PERSISTENCE_TEST_CLIENT_ID = IntegrationClientId("client-123")


def build_persistence_credential(credential_id: str) -> IntegrationCredential:
    """Build one valid active inbound credential for persistence tests."""
    return IntegrationCredential(
        credential_id=IntegrationCredentialId(credential_id),
        client_id=PERSISTENCE_TEST_CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        status=CredentialStatus.ACTIVE,
        issued_at=PERSISTENCE_TEST_ISSUED_AT,
    )
