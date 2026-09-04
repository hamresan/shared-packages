"""Media-type mapping for Meta Instagram media."""

from instagram_api.domain import InstagramMediaType

from .dto import MetaInstagramMediaDto


class MetaInstagramMediaTypeMapper:
    """Maps Meta media/product types to normalized media types."""

    def to_domain(self, dto: MetaInstagramMediaDto) -> InstagramMediaType:
        """Return the normalized media type."""

        if dto.media_product_type == "REELS":
            return InstagramMediaType.REEL
        if dto.media_type == "IMAGE":
            return InstagramMediaType.IMAGE
        if dto.media_type == "VIDEO":
            return InstagramMediaType.VIDEO
        if dto.media_type == "CAROUSEL_ALBUM":
            return InstagramMediaType.CAROUSEL
        return InstagramMediaType.UNKNOWN
