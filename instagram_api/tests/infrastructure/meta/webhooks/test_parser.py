"""Generic Meta Instagram webhook parser tests."""

from datetime import UTC, datetime

import pytest

from instagram_api.domain import (
    InstagramAccountId,
    InstagramCommentChanged,
    InstagramCommentId,
    InstagramMessageReceived,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError
from tests.infrastructure.meta.webhooks.factories import build_meta_webhook_parser


def test_parser_normalizes_changes_and_messaging_for_multiple_accounts() -> None:
    payload = (
        b'{"object":"instagram","entry":['
        b'{"id":"account-a","time":1788523200,"changes":['
        b'{"field":"comments","value":{"id":"comment"}}]},'
        b'{"id":"account-b","time":1788523260,"messaging":['
        b'{"sender":{"id":"user"},"recipient":{"id":"account-b"},'
        b'"timestamp":1788523260000,"message":{"mid":"message","text":"hello"}}]}]}'
    )

    events = build_meta_webhook_parser().parse(payload)

    assert len(events) == 2
    assert events[0].provider_account_id == InstagramAccountId("account-a")
    assert events[0].event_type == "comment:changed"
    assert isinstance(events[0].payload, InstagramCommentChanged)
    assert events[0].payload.comment_id == InstagramCommentId("comment")
    assert events[1].provider_account_id == InstagramAccountId("account-b")
    assert events[1].event_type == "messaging"
    assert isinstance(events[1].payload, InstagramMessageReceived)
    assert events[0].occurred_at == datetime.fromtimestamp(1788523200, tz=UTC)


def test_parser_event_ids_are_deterministic_for_duplicate_delivery() -> None:
    payload = (
        b'{"entry":[{"id":"account","time":1788523200,'
        b'"changes":[{"field":"comments","value":{"id":"comment"}}]}]}'
    )
    parser = build_meta_webhook_parser()

    first = parser.parse(payload)
    second = parser.parse(payload)

    assert first[0].event_id == second[0].event_id


@pytest.mark.parametrize(
    "payload",
    [
        b"not-json",
        b"{}",
        b'{"entry":"invalid"}',
        b'{"entry":[{"time":1,"changes":[]}]}',
    ],
)
def test_parser_rejects_malformed_provider_envelopes(payload: bytes) -> None:
    with pytest.raises(MetaInvalidResponseError):
        build_meta_webhook_parser().parse(payload)
