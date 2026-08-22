"""Credential lifecycle snapshot transitions."""

from dataclasses import replace
from datetime import datetime

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.policies.credential_lifecycle_policy import CredentialLifecyclePolicy


class CredentialLifecycleTransitioner:
    """Create valid immutable credential snapshots for terminal transitions."""

    def __init__(self, lifecycle_policy: CredentialLifecyclePolicy) -> None:
        self._lifecycle_policy = lifecycle_policy

    def revoke(
        self,
        credential: IntegrationCredential,
        revoked_at: datetime,
    ) -> IntegrationCredential:
        self._lifecycle_policy.ensure_transition(
            credential.status,
            CredentialStatus.REVOKED,
        )
        return replace(
            credential,
            status=CredentialStatus.REVOKED,
            revoked_at=revoked_at,
        )

    def expire(
        self,
        credential: IntegrationCredential,
        expires_at: datetime,
    ) -> IntegrationCredential:
        self._lifecycle_policy.ensure_transition(
            credential.status,
            CredentialStatus.EXPIRED,
        )
        return replace(
            credential,
            status=CredentialStatus.EXPIRED,
            expires_at=expires_at,
            revoked_at=None,
        )
