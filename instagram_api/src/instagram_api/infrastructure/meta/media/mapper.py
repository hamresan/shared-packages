"""Mapper for Meta Instagram media DTOs."""

from datetime import datetime

from instagram_api.domain import InstagramMedia, InstagramMediaId, InstagramMediaType
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import MetaInstagramMediaDto


class MetaInstagramMediaMapper:
    """Maps typed Meta media DTOs to normalized domain models."""

    def to_domain(self, dto: MetaInstagramMediaDto) -> InstagramMedia:
        """Map one provider DTO to normalized media."""

        try:
            timestamp = datetime.fromisoformat(dto.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MetaInvalidResponseError(
                message="Meta media response contains an invalid timestamp.",
                status_code=200,
            ) from exc

        return InstagramMedia(
            id=InstagramMediaId(dto.id),
            media_type=self._media_type(dto),
            timestamp=timestamp,
            caption=dto.caption,
            media_url=dto.media_url,
            thumbnail_url=dto.thumbnail_url,
            permalink=dto.permalink,
            children=tuple(InstagramMediaId(child_id) for child_id in dto.children),
        )

    @staticmethod
    def _media_type(dto: MetaInstagramMediaDto) -> InstagramMediaType:
        if dto.media_product_type == "REELS":
            return InstagramMediaType.REEL
        if dto.media_type == "IMAGE":
            return InstagramMediaType.IMAGE
        if dto.media_type == "VIDEO":
            return InstagramMediaType.VIDEO
        if dto.media_type == "CAROUSEL_ALBUM":
            return InstagramMediaType.CAROUSEL
        return InstagramMediaType.UNKNOWN
