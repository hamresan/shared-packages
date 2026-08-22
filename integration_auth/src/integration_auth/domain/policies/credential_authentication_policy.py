"""Credential eligibility policy for request authentication."""

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class CredentialAuthenticationPolicy:
    """Decide whether a credential may authenticate an inbound request."""

    def allows(
        self,
        *,
        credential: IntegrationCredential,
        client_id: IntegrationClientId,
        current_timestamp: int,
    ) -> bool:
        if current_timestamp < 0:
            return False
        if credential.client_id != client_id:
            return False
        if credential.direction is not CredentialDirection.INBOUND:
            return False
        if credential.status is not CredentialStatus.ACTIVE:
            return False
        if int(credential.issued_at.timestamp()) > current_timestamp:
            return False
        if credential.expires_at is not None:
            return int(credential.expires_at.timestamp()) > current_timestamp
        return True
