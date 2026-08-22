"""Builder for credential fixtures used by authentication-service tests."""

from datetime import UTC, datetime, timedelta

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder


class AuthenticationCredentialBuilder:
    """Build an inbound credential valid at a chosen request timestamp."""

    def __init__(self, *, current_timestamp: int) -> None:
        self.credential_id = IntegrationCredentialId("credential-123")
        self.client_id = IntegrationClientId("client-123")
        self.direction = CredentialDirection.INBOUND
        self.current_timestamp = current_timestamp

    def with_credential_id(
        self,
        credential_id: IntegrationCredentialId,
    ) -> "AuthenticationCredentialBuilder":
        self.credential_id = credential_id
        return self

    def with_direction(
        self,
        direction: CredentialDirection,
    ) -> "AuthenticationCredentialBuilder":
        self.direction = direction
        return self

    def build(self) -> IntegrationCredential:
        builder = IntegrationCredentialBuilder()
        builder.credential_id = self.credential_id
        builder.client_id = self.client_id
        builder.direction = self.direction
        builder.issued_at = datetime.fromtimestamp(
            self.current_timestamp,
            tz=UTC,
        ) - timedelta(minutes=1)
        return builder.build()
