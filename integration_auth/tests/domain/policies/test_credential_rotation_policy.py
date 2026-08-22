"""Tests for credential rotation overlap policy."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.policies.credential_rotation_policy import CredentialRotationPolicy
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from tests.support.application.provisioning.rotation_credential_builder import (
    RotationCredentialBuilder,
)

CLIENT_ID = IntegrationClientId("client-123")
NOW = 1787390042
CURRENT_TIME = datetime.fromtimestamp(NOW, tz=UTC)


def test_prepares_matching_active_credential_for_overlap() -> None:
    credential = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).build()

    result = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(credential,),
        client_id=CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        current_timestamp=NOW,
        overlap_seconds=60,
    )

    assert len(result) == 1
    assert result[0].expires_at == CURRENT_TIME + timedelta(seconds=60)


def test_zero_overlap_preserves_domain_expiry_invariant_for_same_second_issue() -> None:
    credential = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).build()
    credential = replace(credential, issued_at=CURRENT_TIME)

    result = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(credential,),
        client_id=CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        current_timestamp=NOW,
        overlap_seconds=0,
    )

    assert result[0].expires_at == CURRENT_TIME + timedelta(microseconds=1)


def test_does_not_extend_earlier_existing_expiry() -> None:
    credential = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).build()
    earlier_expiry = CURRENT_TIME + timedelta(seconds=10)
    credential = replace(credential, expires_at=earlier_expiry)

    result = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(credential,),
        client_id=CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        current_timestamp=NOW,
        overlap_seconds=60,
    )

    assert result[0].expires_at == earlier_expiry


def test_filters_wrong_direction_revoked_and_other_client_credentials() -> None:
    outbound = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).with_direction(CredentialDirection.OUTBOUND).build()
    revoked = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).revoked(NOW).build()
    other = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=IntegrationClientId("client-other"),
    ).build()

    result = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(outbound, revoked, other),
        client_id=CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        current_timestamp=NOW,
        overlap_seconds=60,
    )

    assert result == ()


def test_filters_not_yet_issued_and_already_expired_credentials() -> None:
    base = RotationCredentialBuilder(
        current_timestamp=NOW,
        client_id=CLIENT_ID,
    ).build()
    future = replace(base, issued_at=CURRENT_TIME + timedelta(seconds=30))
    expired = replace(base, expires_at=CURRENT_TIME - timedelta(seconds=1))

    result = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(future, expired),
        client_id=CLIENT_ID,
        direction=CredentialDirection.INBOUND,
        current_timestamp=NOW,
        overlap_seconds=60,
    )

    assert result == ()


@pytest.mark.parametrize(
    ("current_timestamp", "overlap_seconds"),
    [(-1, 0), (0, -1)],
)
def test_rejects_negative_inputs(current_timestamp: int, overlap_seconds: int) -> None:
    with pytest.raises(ValueError):
        CredentialRotationPolicy().prepare_previous_credentials(
            credentials=(),
            client_id=CLIENT_ID,
            direction=CredentialDirection.INBOUND,
            current_timestamp=current_timestamp,
            overlap_seconds=overlap_seconds,
        )
