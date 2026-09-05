"""Provider DTO for Meta Instagram account profile data."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramAccountDto:
    """Typed Meta account profile payload."""

    user_id: str
    username: str
    name: str | None
    biography: str | None
    website: str | None
    profile_picture_url: str | None
    followers_count: int | None
    follows_count: int | None
    media_count: int | None
