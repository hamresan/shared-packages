"""Short-lived one-time OAuth state record."""

from dataclasses import dataclass
from datetime import datetime

from instagram_auth.application.authorization.models.correlation import (
    InstagramAuthorizationCorrelation,
)


@dataclass(frozen=True, slots=True)
class InstagramAuthorizationState:
    """State persisted between authorization start and callback validation."""

    state: str
    redirect_uri: str
    correlation: InstagramAuthorizationCorrelation
    expires_at: datetime
