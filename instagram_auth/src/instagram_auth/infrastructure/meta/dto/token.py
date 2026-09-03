"""Meta token exchange DTO."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramTokenDto:
    """Validated token exchange payload."""

    access_token: str
    expires_in: int | None
    permissions: frozenset[str]
