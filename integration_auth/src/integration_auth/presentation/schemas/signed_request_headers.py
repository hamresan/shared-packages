"""Signed integration request header schema."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SignedRequestHeaders:
    """Validated HTTP header values required for integration authentication."""

    client_id: str
    timestamp: int
    nonce: str
    signature: str
