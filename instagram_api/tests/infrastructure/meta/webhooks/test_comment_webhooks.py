"""Stage 11 Meta comment webhook normalization tests."""

import pytest

from instagram_api.domain import (
    InstagramCommentCreated,
    InstagramCommentId,
    InstagramMediaId,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_parser_normalizes_documented_direct_comment_webhook() -> None:
    payload = (
        b'{"object":"instagram","entry":[{"id":"account","time":1788523200,'
        b'"field":"comments","value":{"id":"comment","from":{'
        b'"id":"commenter","username":"customer"},"text":"Interested",'
        b'"media":{"id":"media","media_product_type":"REELS"}}}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    assert event.event_type == "comment:created"
    assert event.provider_account_id == "account"
    comment = event.payload
    assert isinstance(comment, InstagramCommentCreated)
    assert comment.comment_id == InstagramCommentId("comment")
    assert comment.media_id == InstagramMediaId("media")
    assert comment.commenter_id == InstagramUserId("commenter")
    assert comment.commenter_username == "customer"
    assert comment.text == "Interested"
    assert comment.media_product_type == "REELS"
    assert comment.is_live is False
    assert comment.requires_active_live_broadcast is False


def test_parser_normalizes_live_comment_and_parent_reference() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"field":"live_comments","value":{"id":"reply","from":{'
        b'"username":"customer"},"text":"Live reply","media":{"id":"live-media"},'
        b'"parent_id":"parent-comment"}}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    comment = event.payload
    assert isinstance(comment, InstagramCommentCreated)
    assert comment.comment_id == InstagramCommentId("reply")
    assert comment.parent_comment_id == InstagramCommentId("parent-comment")
    assert comment.commenter_id is None
    assert comment.commenter_username == "customer"
    assert comment.media_id == InstagramMediaId("live-media")
    assert comment.is_live is True
    assert comment.requires_active_live_broadcast is True


def test_parser_normalizes_comment_created_inside_changes_envelope() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,"changes":['
        b'{"field":"comments","value":{"id":"comment","text":"new comment",'
        b'"from":{"id":"commenter"},"media":{"id":"media"}}}]}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    assert event.event_type == "comment:created"
    comment = event.payload
    assert isinstance(comment, InstagramCommentCreated)
    assert comment.comment_id == InstagramCommentId("comment")
    assert comment.commenter_id == InstagramUserId("commenter")
    assert comment.media_id == InstagramMediaId("media")
    assert comment.text == "new comment"


def test_parser_preserves_minimal_comment_for_reader_correlation() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"field":"comments","value":{"id":"comment"}}]}'
    )

    event = build_meta_webhook_parser().parse(payload)[0]

    comment = event.payload
    assert isinstance(comment, InstagramCommentCreated)
    assert comment.comment_id == InstagramCommentId("comment")
    assert comment.media_id is None
    assert comment.commenter_id is None
    assert comment.commenter_username is None
    assert comment.text is None


def test_comment_delivery_event_id_is_stable_for_duplicate_payload() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"field":"comments","value":{"id":"comment","text":"hello"}}]}'
    )
    parser = build_meta_webhook_parser()

    first = parser.parse(payload)[0]
    second = parser.parse(payload)[0]

    assert first.event_id == second.event_id


@pytest.mark.parametrize(
    "payload",
    [
        (b'{"entry":[{"id":"account","field":"comments","value":{"text":"missing comment id"}}]}'),
        (
            b'{"entry":[{"id":"account","changes":['
            b'{"field":"live_comments","value":{"text":"missing id"}}]}]}'
        ),
    ],
)
def test_parser_rejects_comment_payload_without_comment_id(payload: bytes) -> None:
    with pytest.raises(MetaInvalidResponseError):
        build_meta_webhook_parser().parse(payload)
