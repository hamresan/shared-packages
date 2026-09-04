"""Normalized Instagram media models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .identifiers import InstagramMediaId


class InstagramMediaType(StrEnum):
    """Media types exposed by the normalized package boundary."""

    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REEL = "reel"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class InstagramMedia:
    """Provider-neutral representation of owned Instagram media."""

    id: InstagramMediaId
    media_type: InstagramMediaType
    timestamp: datetime
    caption: str | None = None
    media_url: str | None = None
    thumbnail_url: str | None = None
    permalink: str | None = None
    children: tuple[InstagramMediaId, ...] = ()
