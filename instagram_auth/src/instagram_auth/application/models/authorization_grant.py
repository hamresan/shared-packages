"""Transient authorization grant returned by a provider adapter."""

from dataclasses import dataclass
from datetime import datetime

from instagram_auth.baseline import InstagramPermission


@dataclass(frozen=True, slots=True)
class InstagramAuthorizationGrant:
    """Transient provider authorization result before credential protection."""

    access_token: str
    expires_at: datetime | None = None
    granted_permissions: frozenset[InstagramPermission] = frozenset()
