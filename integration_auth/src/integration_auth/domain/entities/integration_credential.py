"""Integration credential domain entity."""

from dataclasses import dataclass
from datetime import datetime

from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.validators.credential_validator import IntegrationCredentialValidator
from integration_auth.domain.validators.datetime_validator import AwareDateTimeValidator
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)

_CREDENTIAL_VALIDATOR = IntegrationCredentialValidator(AwareDateTimeValidator())


@dataclass(frozen=True, slots=True)
class IntegrationCredential:
    """Credential metadata without cryptographic secret material."""

    credential_id: IntegrationCredentialId
    client_id: IntegrationClientId
    direction: CredentialDirection
    status: CredentialStatus
    issued_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        _CREDENTIAL_VALIDATOR.validate(
            status=self.status,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
        )
