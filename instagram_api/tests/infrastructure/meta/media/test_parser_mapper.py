"""Meta media parser and mapper tests."""

import pytest

from instagram_api.domain import InstagramMediaId, InstagramMediaType
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError
from instagram_api.infrastructure.meta.media import (
    MetaInstagramMediaFieldParser,
    MetaInstagramMediaMapper,
    MetaInstagramMediaPayloadParser,
    MetaInstagramMediaTimestampParser,
    MetaInstagramMediaTypeMapper,
)


def build_parser() -> MetaInstagramMediaPayloadParser:
    return MetaInstagramMediaPayloadParser(MetaInstagramMediaFieldParser())


def build_mapper() -> MetaInstagramMediaMapper:
    return MetaInstagramMediaMapper(
        MetaInstagramMediaTypeMapper(),
        MetaInstagramMediaTimestampParser(),
    )


@pytest.mark.parametrize(
    ("media_type", "product_type", "expected"),
    [
        ("IMAGE", "FEED", InstagramMediaType.IMAGE),
        ("VIDEO", "FEED", InstagramMediaType.VIDEO),
        ("VIDEO", "REELS", InstagramMediaType.REEL),
        ("CAROUSEL_ALBUM", "FEED", InstagramMediaType.CAROUSEL),
        ("OTHER", None, InstagramMediaType.UNKNOWN),
    ],
)
def test_parser_mapper_normalizes_media_types(
    media_type: str,
    product_type: str | None,
    expected: InstagramMediaType,
) -> None:
    dto = build_parser().parse_media(
        {
            "id": "media",
            "media_type": media_type,
            "media_product_type": product_type,
            "timestamp": "2026-09-04T10:00:00+0000",
            "caption": "Caption",
            "children": {"data": [{"id": "child-1"}, {"id": "child-2"}]},
        }
    )
    media = build_mapper().to_domain(dto)

    assert media.id == InstagramMediaId("media")
    assert media.media_type is expected
    assert media.caption == "Caption"
    assert media.children == (
        InstagramMediaId("child-1"),
        InstagramMediaId("child-2"),
    )


def test_parser_rejects_invalid_collection_and_required_fields() -> None:
    parser = build_parser()

    with pytest.raises(MetaInvalidResponseError):
        parser.parse_media_list({"data": "invalid"})

    with pytest.raises(MetaInvalidResponseError):
        parser.parse_media({"id": "media", "media_type": "IMAGE"})


def test_mapper_rejects_invalid_timestamp() -> None:
    dto = build_parser().parse_media(
        {
            "id": "media",
            "media_type": "IMAGE",
            "timestamp": "not-a-timestamp",
        }
    )

    with pytest.raises(MetaInvalidResponseError):
        build_mapper().to_domain(dto)
