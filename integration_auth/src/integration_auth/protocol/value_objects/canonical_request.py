"""Canonical request value object."""

from dataclasses import dataclass

from integration_auth.protocol.validators.canonical_request_validator import CanonicalRequestValidator

_CANONICAL_REQUEST_VALIDATOR = CanonicalRequestValidator()


@dataclass(frozen=True, slots=True)
class CanonicalRequest:
    """Immutable values covered by an integration request signature."""

    method: str
    path: str
    canonical_query: str
    timestamp: int
    nonce: str
    body_sha256: str

    def __post_init__(self) -> None:
        _CANONICAL_REQUEST_VALIDATOR.validate(
            method=self.method,
            path=self.path,
            canonical_query=self.canonical_query,
            timestamp=self.timestamp,
            nonce=self.nonce,
            body_sha256=self.body_sha256,
        )
