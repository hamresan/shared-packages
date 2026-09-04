"""Normalized Instagram account models."""

from dataclasses import dataclass

from .identifiers import InstagramAccountId


@dataclass(frozen=True, slots=True)
class InstagramAccount:
    """Provider-neutral Instagram Professional account profile."""

    id: InstagramAccountId
    username: str
    name: str | None = None
    biography: str | None = None
    website: str | None = None
    profile_picture_url: str | None = None
    followers_count: int | None = None
    follows_count: int | None = None
    media_count: int | None = None
