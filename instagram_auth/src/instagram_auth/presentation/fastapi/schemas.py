"""HTTP response schemas for the optional FastAPI adapter."""

from datetime import datetime

from pydantic import BaseModel

from instagram_auth.baseline import InstagramAccountType, InstagramConnectionState, InstagramPermission


class InstagramAuthorizationStartResponse(BaseModel):
    authorization_url: str
    expires_at: datetime


class InstagramConnectionResponse(BaseModel):
    id: str
    instagram_account_id: str
    username: str
    account_type: InstagramAccountType
    permissions: list[InstagramPermission]
    status: InstagramConnectionState
    connected_at: datetime
    credential_expires_at: datetime | None
    revoked_at: datetime | None
    last_validated_at: datetime | None
    version: int
