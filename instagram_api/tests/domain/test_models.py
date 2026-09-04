"""Normalized model tests."""

from datetime import UTC, datetime

from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    InstagramMediaType,
    InstagramWebhookEvent,
    Page,
    PaginationCursor,
)


def test_normalized_models_preserve_opaque_ids_and_optional_fields() -> None:
    connection_id = InstagramConnectionId("local-connection")
    account_id = InstagramAccountId("17841400000000000")
    media_id = InstagramMediaId("17900000000000000")
    timestamp = datetime.now(UTC)

    connection = InstagramConnection(
        id=connection_id,
        provider_account_id=account_id,
        permissions=frozenset({"instagram_business_basic"}),
        is_usable=True,
    )
    account = InstagramAccount(
        id=account_id,
        username="shop",
        biography="Bio",
        followers_count=10,
    )
    media = InstagramMedia(
        id=media_id,
        media_type=InstagramMediaType.REEL,
        timestamp=timestamp,
        caption="Caption",
    )

    assert connection.id == connection_id
    assert connection.provider_account_id == account_id
    assert account.biography == "Bio"
    assert account.website is None
    assert media.caption == "Caption"
    assert media.children == ()


def test_page_and_webhook_event_are_provider_neutral() -> None:
    cursor = PaginationCursor("next-cursor")
    event = InstagramWebhookEvent(
        event_id="event-1",
        event_type="message_received",
        provider_account_id=InstagramAccountId("ig-account"),
    )
    page = Page(items=(event,), next_cursor=cursor)

    assert page.items == (event,)
    assert page.next_cursor == cursor
    assert event.occurred_at is None
