"""Validated callback correlation model."""

from dataclasses import dataclass

from instagram_auth.application.authorization.models.correlation import (
    InstagramAuthorizationCorrelation,
)


@dataclass(frozen=True, slots=True)
class ValidatedInstagramAuthorization:
    """Trusted correlation context recovered from a validated callback state."""

    redirect_uri: str
    correlation: InstagramAuthorizationCorrelation
