"""Meta Instagram comment parser tests."""

import pytest

from instagram_api.infrastructure.meta.comments import (
    MetaInstagramCommentFieldParser,
    MetaInstagramCommentPayloadParser,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


def test_parser_uses_fallback_media_and_parent_ids_when_edges_omit_them() -> None:
    parser = MetaInstagramCommentPayloadParser(MetaInstagramCommentFieldParser())

    dto = parser.parse_comment(
        {
            "id": "reply",
            "text": "hello",
            "timestamp": "2026-09-04T10:00:00+0000",
            "from": {"id": "author"},
        },
        fallback_media_id="media",
        fallback_parent_id="parent",
    )

    assert dto.media_id == "media"
    assert dto.parent_comment_id == "parent"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": "invalid"},
    ],
)
def test_parser_rejects_invalid_payloads(payload: dict[str, object]) -> None:
    parser = MetaInstagramCommentPayloadParser(MetaInstagramCommentFieldParser())

    with pytest.raises(MetaInvalidResponseError):
        if "data" in payload:
            parser.parse_collection(payload)
        else:
            parser.parse_comment(payload)
