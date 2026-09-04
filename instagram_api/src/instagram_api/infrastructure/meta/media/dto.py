"""Provider DTOs for Meta Instagram media data."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramMediaDto:
    """Typed Meta media payload."""

    id: str
    media_type: str
    media_product_type: str | None
    timestamp: str
    caption: str | None
    media_url: str | None
    thumbnail_url: str | None
    permalink: str | None
    children: tuple[str, ...]
