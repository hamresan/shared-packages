"""Credential lifecycle transition policy."""

from integration_auth.domain.enums.credential_status import CredentialStatus


class CredentialLifecyclePolicy:
    """Define allowed credential lifecycle transitions."""

    _ALLOWED_TRANSITIONS: dict[CredentialStatus, frozenset[CredentialStatus]] = {
        CredentialStatus.ACTIVE: frozenset(
            {CredentialStatus.REVOKED, CredentialStatus.EXPIRED}
        ),
        CredentialStatus.REVOKED: frozenset(),
        CredentialStatus.EXPIRED: frozenset(),
    }

    def can_transition(
        self,
        current_status: CredentialStatus,
        target_status: CredentialStatus,
    ) -> bool:
        """Return whether the requested lifecycle transition is valid."""
        return target_status in self._ALLOWED_TRANSITIONS[current_status]

    def ensure_transition(
        self,
        current_status: CredentialStatus,
        target_status: CredentialStatus,
    ) -> None:
        """Raise ``ValueError`` when a lifecycle transition is not allowed."""
        if not self.can_transition(current_status, target_status):
            raise ValueError(
                f"credential status cannot transition from {current_status.value} "
                f"to {target_status.value}"
            )
