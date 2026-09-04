"""Instagram media service tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.media import (
    InstagramMediaAccessPolicy,
    InstagramMediaConnectionUnavailableError,
    InstagramMediaPermissionRequiredError,
    InstagramMediaService,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    InstagramMediaType,
    Page,
    PaginationCursor,
)
from tests.fakes import FakeInstagramConnectionReader, FakeInstagramMediaProvider


def build_connection(
    connection_id: InstagramConnectionId,
    account_id: InstagramAccountId,
    *,
    usable: bool = True,
    permissions: frozenset[str] = frozenset({"instagram_business_basic"}),
) -> InstagramConnection:
    return InstagramConnection(
        id=connection_id,
        provider_account_id=account_id,
        permissions=permissions,
        is_usable=usable,
    )


def test_service_keeps_two_connections_isolated_and_passes_cursor() -> None:
    now = datetime.now(UTC)
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    first_media = InstagramMedia(
        InstagramMediaId("media-a"),
        InstagramMediaType.IMAGE,
        now,
    )
    second_media = InstagramMedia(
        InstagramMediaId("media-b"),
        InstagramMediaType.REEL,
        now,
    )
    provider = FakeInstagramMediaProvider(
        {
            first_id: Page(items=(first_media,), next_cursor=PaginationCursor("next-a")),
            second_id: Page(items=(second_media,)),
        }
    )
    service = InstagramMediaService(
        FakeInstagramConnectionReader(
            {
                first_id: build_connection(first_id, InstagramAccountId("account-a")),
                second_id: build_connection(second_id, InstagramAccountId("account-b")),
            }
        ),
        provider,
        InstagramMediaAccessPolicy(),
    )

    first_page = asyncio.run(service.list_media(first_id, PaginationCursor("cursor-a")))
    second_item = asyncio.run(service.get_media(second_id, second_media.id))

    assert first_page.items == (first_media,)
    assert first_page.next_cursor == PaginationCursor("next-a")
    assert second_item == second_media
    assert provider.list_calls == [(first_id, PaginationCursor("cursor-a"))]
    assert provider.get_calls == [(second_id, second_media.id)]


@pytest.mark.parametrize(
    ("usable", "permissions", "error_type"),
    [
        (False, frozenset({"instagram_business_basic"}), InstagramMediaConnectionUnavailableError),
        (True, frozenset(), InstagramMediaPermissionRequiredError),
    ],
)
def test_service_rejects_ineligible_connection_before_provider_call(
    usable: bool,
    permissions: frozenset[str],
    error_type: type[Exception],
) -> None:
    connection_id = InstagramConnectionId("connection")
    provider = FakeInstagramMediaProvider({connection_id: Page(items=())})
    service = InstagramMediaService(
        FakeInstagramConnectionReader(
            {
                connection_id: build_connection(
                    connection_id,
                    InstagramAccountId("account"),
                    usable=usable,
                    permissions=permissions,
                )
            }
        ),
        provider,
        InstagramMediaAccessPolicy(),
    )

    with pytest.raises(error_type):
        asyncio.run(service.list_media(connection_id))

    assert provider.list_calls == []
