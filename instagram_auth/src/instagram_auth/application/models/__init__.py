"""Application models for Instagram authentication."""

from instagram_auth.application.models.authorization_grant import InstagramAuthorizationGrant
from instagram_auth.application.models.protected_credential import InstagramProtectedCredential

__all__ = ["InstagramAuthorizationGrant", "InstagramProtectedCredential"]
