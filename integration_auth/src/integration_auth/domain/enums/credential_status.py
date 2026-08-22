"""Credential lifecycle states."""

from enum import StrEnum


class CredentialStatus(StrEnum):
    """Current lifecycle state of an integration credential."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
