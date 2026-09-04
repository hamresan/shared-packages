"""End-to-end reference consumer test for two Instagram connections."""

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine

from identity import AuthenticatedPrincipal
from instagram_api.application.webhooks import (
    InstagramWebhookProcessor,
    NullInstagramWebhookOperationalObserver,
    RetryInstagramWebhookFailureHandler,
)
from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramCommentCreated,
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMessageId,
    InstagramMessageReceived,
    InstagramUserId,
    InstagramWebhookEvent,
)
from instagram_auth import (
    CORE_PERMISSIONS,
    InstagramAccountType,
    InstagramConnection,
    InstagramConnectionId as AuthInstagramConnectionId,
    InstagramConnectionState,
)
from instagram_sales_host_consumer_app.composition import build_reference_runtime
from instagram_sales_host_consumer_app.persistence import HostSchema
from tests.support import (
    FakeAccountProvider,
    FakeAuthAccessTokenProvider,
    FakeAuthConnectionReader,
    FakeMediaProvider,
    RecordingCommentReplyProvider,
    RecordingMessageProvider,
)
from tests.support.instagram_api import build_media
from tests.support.webhooks import (
    AcceptingWebhookVerifier,
    InMemoryWebhookIdempotencyStore,
    StaticWebhookParser,
)

USER_ID = UUID("00000000-0000-0000-0000-000000000001")
SESSION_ID = UUID("00000000-0000-0000-0000-000000000002")
AUTH_CONNECTION_A = AuthInstagramConnectionId(
    UUID("00000000-0000-0000-0000-000000000011")
)
AUTH_CONNECTION_B = AuthInstagramConnectionId(
    UUID("00000000-0000-0000-0000-000000000012")
)
API_CONNECTION_A = InstagramConnectionId(str(AUTH_CONNECTION_A.value))
API_CONNECTION_B = InstagramConnectionId(str(AUTH_CONNECTION_B.value))


def build_auth_connection(
    connection_id: AuthInstagramConnectionId,
    account_id: str,
    username: str,
) -> InstagramConnection:
    """Build one independent auth-owned connection."""

    return InstagramConnection(
        id=connection_id,
        owner_user_id=str(USER_ID),
        instagram_account_id=account_id,
        username=username,
        account_type=InstagramAccountType.BUSINESS,
        permissions=CORE_PERMISSIONS,
        status=InstagramConnectionState.CONNECTED,
        connected_at=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
    )


def build_principal() -> AuthenticatedPrincipal:
    """Build the identity package principal consumed by the host."""

    issued_at = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)
    return AuthenticatedPrincipal(
        user_id=USER_ID,
        session_id=SESSION_ID,
        authentication_method="instagram-host-bootstrap",
        issued_at=issued_at,
        expires_at=issued_at + timedelta(hours=1),
    )


def test_two_connections_remain_isolated_across_reads_webhooks_and_replies(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'host.db'}"
        )
        message_provider = RecordingMessageProvider()
        comment_provider = RecordingCommentReplyProvider()
        try:
            await HostSchema(engine).create()

            connection_a = build_auth_connection(
                AUTH_CONNECTION_A,
                "ig-account-a",
                "shop_a",
            )
            connection_b = build_auth_connection(
                AUTH_CONNECTION_B,
                "ig-account-b",
                "shop_b",
            )
            runtime = build_reference_runtime(
                engine=engine,
                auth_connection_reader=FakeAuthConnectionReader(
                    {
                        AUTH_CONNECTION_A: connection_a,
                        AUTH_CONNECTION_B: connection_b,
                    }
                ),
                auth_access_token_provider=FakeAuthAccessTokenProvider(
                    {
                        AUTH_CONNECTION_A: "token-a",
                        AUTH_CONNECTION_B: "token-b",
                    }
                ),
                account_provider=FakeAccountProvider(
                    {
                        API_CONNECTION_A: InstagramAccount(
                            id=InstagramAccountId("ig-account-a"),
                            username="shop_a",
                            biography="First account",
                        ),
                        API_CONNECTION_B: InstagramAccount(
                            id=InstagramAccountId("ig-account-b"),
                            username="shop_b",
                            biography="Second account",
                        ),
                    }
                ),
                media_provider=FakeMediaProvider(
                    {
                        API_CONNECTION_A: (build_media("media-a", "A caption"),),
                        API_CONNECTION_B: (build_media("media-b", "B caption"),),
                    }
                ),
                recipient_eligibility_checker=message_provider,
                outbound_message_provider=message_provider,
                public_comment_reply_provider=comment_provider,
            )

            principal = build_principal()
            await runtime.connection_registry.link(
                principal,
                API_CONNECTION_A,
                InstagramAccountId("ig-account-a"),
            )
            await runtime.connection_registry.link(
                principal,
                API_CONNECTION_B,
                InstagramAccountId("ig-account-b"),
            )

            owner_connections = await runtime.connection_registry.list_owner_connections(
                principal
            )
            assert set(owner_connections) == {API_CONNECTION_A, API_CONNECTION_B}

            account_a = await runtime.account_service.get_account(API_CONNECTION_A)
            account_b = await runtime.account_service.get_account(API_CONNECTION_B)
            assert account_a.username == "shop_a"
            assert account_b.username == "shop_b"

            media_a = await runtime.media_service.list_media(API_CONNECTION_A)
            media_b = await runtime.media_service.list_media(API_CONNECTION_B)
            assert media_a.items[0].caption == "A caption"
            assert media_b.items[0].caption == "B caption"

            assert (
                await runtime.access_token_provider.get_access_token(API_CONNECTION_A)
                == "token-a"
            )
            assert (
                await runtime.access_token_provider.get_access_token(API_CONNECTION_B)
                == "token-b"
            )

            dm_event = InstagramWebhookEvent(
                event_id="dm-event",
                event_type="messaging",
                provider_account_id=InstagramAccountId("ig-account-a"),
                payload=InstagramMessageReceived(
                    sender_id=InstagramUserId("customer-a"),
                    recipient_id=InstagramUserId("ig-account-a"),
                    occurred_at=datetime(2026, 9, 4, 12, 1, tzinfo=UTC),
                    message_id=InstagramMessageId("message-a"),
                    text="Hello",
                ),
            )
            dm_processor = InstagramWebhookProcessor(
                AcceptingWebhookVerifier(),
                StaticWebhookParser(dm_event),
                InMemoryWebhookIdempotencyStore(),
                runtime.connection_registry,
                runtime.automation_dispatcher,
                RetryInstagramWebhookFailureHandler(),
                NullInstagramWebhookOperationalObserver(),
            )
            assert await dm_processor.process(b"dm", "signature") == 1

            comment_event = InstagramWebhookEvent(
                event_id="comment-event",
                event_type="comment:created",
                provider_account_id=InstagramAccountId("ig-account-b"),
                payload=InstagramCommentCreated(
                    comment_id=InstagramCommentId("comment-b"),
                    media_id=None,
                    commenter_id=InstagramUserId("customer-b"),
                    commenter_username="customer_b",
                    text="Nice",
                ),
            )
            comment_processor = InstagramWebhookProcessor(
                AcceptingWebhookVerifier(),
                StaticWebhookParser(comment_event),
                InMemoryWebhookIdempotencyStore(),
                runtime.connection_registry,
                runtime.automation_dispatcher,
                RetryInstagramWebhookFailureHandler(),
                NullInstagramWebhookOperationalObserver(),
            )
            assert await comment_processor.process(b"comment", "signature") == 1

            assert message_provider.sent[0][0] == API_CONNECTION_A
            assert message_provider.sent[0][1].recipient_id == InstagramUserId(
                "customer-a"
            )
            assert comment_provider.replies == [
                (
                    API_CONNECTION_B,
                    InstagramCommentId("comment-b"),
                    "Thanks for your comment.",
                )
            ]
        finally:
            await engine.dispose()

    asyncio.run(scenario())
