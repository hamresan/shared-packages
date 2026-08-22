"""Validation for integration credential snapshots."""

from datetime import datetime

from integration_auth.domain.enums.credential_status import CredentialStatus


class IntegrationCredentialValidator:
    """Validate lifecycle invariants of an integration credential snapshot."""

    def validate(
        self,
        *,
        status: CredentialStatus,
        issued_at: datetime,
        expires_at: datetime | None,
        revoked_at: datetime | None,
    ) -> None:
        """Raise ``ValueError`` when the credential snapshot is inconsistent."""
        self._require_timezone(issued_at, field_name="issued_at")
        if expires_at is not None:
            self._require_timezone(expires_at, field_name="expires_at")
            if expires_at <= issued_at:
                raise ValueError("expires_at must be later than issued_at")
        if revoked_at is not None:
            self._require_timezone(revoked_at, field_name="revoked_at")
            if revoked_at < issued_at:
                raise ValueError("revoked_at must not be earlier than issued_at")

        if status is CredentialStatus.ACTIVE and revoked_at is not None:
            raise ValueError("an active credential cannot have revoked_at")
        if status is CredentialStatus.REVOKED and revoked_at is None:
            raise ValueError("a revoked credential requires revoked_at")
        if status is CredentialStatus.EXPIRED:
            if expires_at is None:
                raise ValueError("an expired credential requires expires_at")
            if revoked_at is not None:
                raise ValueError("an expired credential cannot have revoked_at")

    @staticmethod
    def _require_timezone(value: datetime, *, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
