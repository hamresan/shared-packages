"""Mapper for Meta Instagram media DTOs."""

from instagram_api.domain import InstagramMedia, InstagramMediaId

from .dto import MetaInstagramMediaDto
from .timestamp_parser import MetaInstagramMediaTimestampParser
from .type_mapper import MetaInstagramMediaTypeMapper


class MetaInstagramMediaMapper:
    """Maps typed Meta media DTOs to normalized domain models."""

    def __init__(
        self,
        type_mapper: MetaInstagramMediaTypeMapper,
        timestamp_parser: MetaInstagramMediaTimestampParser,
    ) -> None:
        self._type_mapper = type_mapper
        self._timestamp_parser = timestamp_parser

    def to_domain(self, dto: MetaInstagramMediaDto) -> InstagramMedia:
        """Map one provider DTO to normalized media."""

        return InstagramMedia(
            id=InstagramMediaId(dto.id),
            media_type=self._type_mapper.to_domain(dto),
            timestamp=self._timestamp_parser.parse(dto.timestamp),
            caption=dto.caption,
            media_url=dto.media_url,
            thumbnail_url=dto.thumbnail_url,
            permalink=dto.permalink,
            children=tuple(InstagramMediaId(child_id) for child_id in dto.children),
        )
