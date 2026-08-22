"""Tests for credential lifecycle transition policy."""

import pytest

from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.policies.credential_lifecycle_policy import CredentialLifecyclePolicy


@pytest.mark.parametrize(
    "target_status",
    [CredentialStatus.REVOKED, CredentialStatus.EXPIRED],
)
def test_active_credential_can_transition_to_terminal_status(
    target_status: CredentialStatus,
) -> None:
    policy = CredentialLifecyclePolicy()

    assert policy.can_transition(CredentialStatus.ACTIVE, target_status)
    policy.ensure_transition(CredentialStatus.ACTIVE, target_status)


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        (CredentialStatus.ACTIVE, CredentialStatus.ACTIVE),
        (CredentialStatus.REVOKED, CredentialStatus.ACTIVE),
        (CredentialStatus.REVOKED, CredentialStatus.EXPIRED),
        (CredentialStatus.EXPIRED, CredentialStatus.ACTIVE),
        (CredentialStatus.EXPIRED, CredentialStatus.REVOKED),
    ],
)
def test_rejects_invalid_lifecycle_transition(
    current_status: CredentialStatus,
    target_status: CredentialStatus,
) -> None:
    policy = CredentialLifecyclePolicy()

    assert not policy.can_transition(current_status, target_status)
    with pytest.raises(ValueError, match="credential status cannot transition"):
        policy.ensure_transition(current_status, target_status)
