"""Reusable fakes for Instagram API tests."""

from .accounts import FakeInstagramAccountProvider, FakeInstagramAccountReader
from .clocks import FixedInstagramReplyClock
from .comments import (
    FakeInstagramCommentProvider,
    FakeInstagramCommentReader,
    FakeInstagramCommentReplier,
    FakeInstagramPrivateCommentReplyProvider,
    FakeInstagramPublicCommentReplyProvider,
)
from .connections import FakeInstagramAccessTokenProvider, FakeInstagramConnectionReader
from .media import FakeInstagramMediaProvider, FakeInstagramMediaReader
from .messaging import (
    FakeInstagramConversationProvider,
    FakeInstagramConversationReader,
    FakeInstagramMessageProvider,
    FakeInstagramMessageReader,
    FakeInstagramMessageRecipientEligibilityChecker,
    FakeInstagramMessageSender,
    FakeInstagramOutboundMessageProvider,
)
from .webhooks import (
    FakeInstagramMessagingWebhookHandler,
    FakeInstagramWebhookConnectionResolver,
    FakeInstagramWebhookEventDispatcher,
    FakeInstagramWebhookIdempotencyStore,
    FakeInstagramWebhookParser,
    FakeInstagramWebhookVerifier,
)

__all__ = [
    "FakeInstagramAccessTokenProvider",
    "FakeInstagramAccountProvider",
    "FakeInstagramAccountReader",
    "FakeInstagramCommentProvider",
    "FakeInstagramCommentReader",
    "FakeInstagramCommentReplier",
    "FakeInstagramPrivateCommentReplyProvider",
    "FakeInstagramPublicCommentReplyProvider",
    "FixedInstagramReplyClock",
    "FakeInstagramConnectionReader",
    "FakeInstagramConversationProvider",
    "FakeInstagramConversationReader",
    "FakeInstagramMediaProvider",
    "FakeInstagramMediaReader",
    "FakeInstagramMessageProvider",
    "FakeInstagramMessageRecipientEligibilityChecker",
    "FakeInstagramMessageReader",
    "FakeInstagramMessageSender",
    "FakeInstagramOutboundMessageProvider",
    "FakeInstagramMessagingWebhookHandler",
    "FakeInstagramWebhookConnectionResolver",
    "FakeInstagramWebhookEventDispatcher",
    "FakeInstagramWebhookIdempotencyStore",
    "FakeInstagramWebhookParser",
    "FakeInstagramWebhookVerifier",
]
