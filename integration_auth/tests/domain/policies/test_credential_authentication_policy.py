"""Tests for credential authentication eligibility policy."""

from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.policies.credential_authentication_policy import (
    CredentialAuthenticationPolicy,
)
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)

NOW = datetime(2026, 8, 22, 15, 0, tzinfo=UTC)
NOW_TIMESTAMP = int(NOW.timestamp())
CLIENT_ID = IntegrationClientId("client-123")


def build_credential(
    *,
    client_id: IntegrationClientId = CLIENT_ID,
    direction: CredentialDirection = CredentialDirection.INBOUND,
    status: CredentialStatus = CredentialStatus.ACTIVE,
    issued_at: datetime | None = None,
    expires_at: datetime | None = None,
    revoked_at: datetime | None = None,
) -> IntegrationCredential:
    return IntegrationCredential(
        credential_id=IntegrationCredentialId("credential-123"),
        client_id=client_id,
        direction=direction,
        status=status,
        issued_at=issued_at or NOW - timedelta(minutes=1),
        expires_at=expires_at,
        revoked_at=revoked_at,
    )


def test_allows_active_inbound_credential_for_same_client() -> None:
    assert CredentialAuthenticationPolicy().allows(
        credential=build_credential(),
        client_id=CLIENT_ID,
        current_timestamp=NOW_TIMESTAMP,
    )


@pytest.mark.parametrize(
    "credential",
    [
        build_credential(client_id=IntegrationClientId("other-client")),
        build_credential(direction=CredentialDirection.OUTBOUND),
        build_credential(
            status=CredentialStatus.REVOKED,
            revoked_at=NOW - timedelta(seconds=1),
        ),
        build_credential(issued_at=NOW + timedelta(seconds=1)),
        build_credential(expires_at=NOW),
    ],
)
def test_rejects_credential_not_usable_for_inbound_authentication(
    credential: IntegrationCredential,
) -> None:
    assert not CredentialAuthenticationPolicy().allows(
        credential=credential,
        client_id=CLIENT_ID,
        current_timestamp=NOW_TIMESTAMP,
    )


def test_rejects_negative_current_timestamp() -> None:
    assert not CredentialAuthenticationPolicy().allows(
        credential=build_credential(),
        client_id=CLIENT_ID,
        current_timestamp=-1,
    )
