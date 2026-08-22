"""Credential rotation overlap policy."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class CredentialRotationPolicy:
    """Prepare currently usable same-direction credentials for rotation overlap."""

    def prepare_previous_credentials(
        self,
        *,
        credentials: tuple[IntegrationCredential, ...],
        client_id: IntegrationClientId,
        direction: CredentialDirection,
        current_timestamp: int,
        overlap_seconds: int,
    ) -> tuple[IntegrationCredential, ...]:
        if current_timestamp < 0:
            raise ValueError("current_timestamp must be non-negative")
        if overlap_seconds < 0:
            raise ValueError("overlap_seconds must be non-negative")

        current_time = datetime.fromtimestamp(current_timestamp, tz=UTC)
        overlap_end = current_time + timedelta(seconds=overlap_seconds)
        prepared: list[IntegrationCredential] = []

        for credential in credentials:
            if credential.client_id != client_id:
                continue
            if credential.direction is not direction:
                continue
            if credential.status is not CredentialStatus.ACTIVE:
                continue
            if credential.issued_at > current_time:
                continue
            if credential.expires_at is not None and credential.expires_at <= current_time:
                continue

            expires_at = overlap_end
            minimum_expiry = credential.issued_at + timedelta(microseconds=1)
            if expires_at < minimum_expiry:
                expires_at = minimum_expiry
            if credential.expires_at is not None and credential.expires_at < expires_at:
                expires_at = credential.expires_at
            prepared.append(replace(credential, expires_at=expires_at))

        return tuple(prepared)
