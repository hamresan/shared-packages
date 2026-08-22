"""Credential request direction."""

from enum import StrEnum


class CredentialDirection(StrEnum):
    """Direction in which a credential is intended to authenticate requests."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"
