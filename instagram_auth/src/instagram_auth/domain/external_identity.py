"""Resolved Instagram external identity."""

from dataclasses import dataclass
from typing import ClassVar

from instagram_auth.baseline import InstagramAccountType


@dataclass(frozen=True, slots=True)
class InstagramExternalIdentity:
    """Stable provider identity resolved from an Instagram authorization."""

    provider_user_id: str
    username: str
    account_type: InstagramAccountType
    provider: ClassVar[str] = "instagram"
