"""Authorization-start input and output models."""

from collections.abc import Collection
from dataclasses import dataclass
from datetime import datetime

from instagram_auth.application.authorization.models.correlation import (
    InstagramAuthorizationCorrelation,
)
from instagram_auth.baseline import InstagramPermission


@dataclass(frozen=True, slots=True)
class StartInstagramAuthorizationCommand:
    """Host input required to start an Instagram authorization attempt."""

    redirect_uri: str
    correlation: InstagramAuthorizationCorrelation
    optional_permissions: Collection[InstagramPermission] = ()


@dataclass(frozen=True, slots=True)
class InstagramAuthorizationStartResult:
    """Redirect information returned to the host application."""

    authorization_url: str
    expires_at: datetime
