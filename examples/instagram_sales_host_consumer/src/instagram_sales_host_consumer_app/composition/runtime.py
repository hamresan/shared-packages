"""Host composition using only public contracts from reusable packages."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from instagram_api.application.accounts import (
    InstagramAccountAccessPolicy,
    InstagramAccountService,
)
from instagram_api.application.comments import (
    InstagramCommentReplyAccessPolicy,
    InstagramCommentReplyTextPolicy,
    InstagramPublicCommentReplyService,
)
from instagram_api.application.contracts import (
    InstagramAccountProvider,
    InstagramMediaProvider,
    InstagramMessageRecipientEligibilityChecker,
    InstagramOutboundMessageProvider,
    InstagramPublicCommentReplyProvider,
)
from instagram_api.application.media import (
    InstagramMediaAccessPolicy,
    InstagramMediaService,
)
from instagram_api.application.messaging import (
    InstagramMessagePayloadPolicy,
    InstagramMessageSendAccessPolicy,
    InstagramMessageSendService,
)
from instagram_auth import (
    InstagramAccessTokenProvider as AuthInstagramAccessTokenProvider,
)
from instagram_auth import InstagramConnectionReader as AuthInstagramConnectionReader

from instagram_sales_host_consumer_app.auth_adapters import (
    InstagramAuthAccessTokenAdapter,
    InstagramAuthConnectionAdapter,
)
from instagram_sales_host_consumer_app.automation import HostAutomationDispatcher
from instagram_sales_host_consumer_app.persistence import (
    SqlAlchemyHostConnectionRegistry,
)


@dataclass(frozen=True, slots=True)
class ReferenceInstagramRuntime:
    """Reference host services composed across package boundaries."""

    connection_registry: SqlAlchemyHostConnectionRegistry
    connection_reader: InstagramAuthConnectionAdapter
    access_token_provider: InstagramAuthAccessTokenAdapter
    account_service: InstagramAccountService
    media_service: InstagramMediaService
    message_service: InstagramMessageSendService
    comment_reply_service: InstagramPublicCommentReplyService
    automation_dispatcher: HostAutomationDispatcher


def build_reference_runtime(
    *,
    engine: AsyncEngine,
    auth_connection_reader: AuthInstagramConnectionReader,
    auth_access_token_provider: AuthInstagramAccessTokenProvider,
    account_provider: InstagramAccountProvider,
    media_provider: InstagramMediaProvider,
    recipient_eligibility_checker: InstagramMessageRecipientEligibilityChecker,
    outbound_message_provider: InstagramOutboundMessageProvider,
    public_comment_reply_provider: InstagramPublicCommentReplyProvider,
) -> ReferenceInstagramRuntime:
    """Compose the reference consumer without package-to-package persistence access."""

    connection_reader = InstagramAuthConnectionAdapter(auth_connection_reader)
    access_token_provider = InstagramAuthAccessTokenAdapter(
        auth_access_token_provider
    )
    account_service = InstagramAccountService(
        connection_reader,
        account_provider,
        InstagramAccountAccessPolicy(),
    )
    media_service = InstagramMediaService(
        connection_reader,
        media_provider,
        InstagramMediaAccessPolicy(),
    )
    message_service = InstagramMessageSendService(
        connection_reader,
        recipient_eligibility_checker,
        outbound_message_provider,
        InstagramMessageSendAccessPolicy(),
        InstagramMessagePayloadPolicy(),
    )
    comment_reply_service = InstagramPublicCommentReplyService(
        connection_reader,
        public_comment_reply_provider,
        InstagramCommentReplyAccessPolicy(),
        InstagramCommentReplyTextPolicy(),
    )
    automation_dispatcher = HostAutomationDispatcher(
        message_service,
        comment_reply_service,
    )
    return ReferenceInstagramRuntime(
        connection_registry=SqlAlchemyHostConnectionRegistry(engine),
        connection_reader=connection_reader,
        access_token_provider=access_token_provider,
        account_service=account_service,
        media_service=media_service,
        message_service=message_service,
        comment_reply_service=comment_reply_service,
        automation_dispatcher=automation_dispatcher,
    )
