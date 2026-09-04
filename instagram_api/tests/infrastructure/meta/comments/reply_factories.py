"""Factories for Meta Instagram comment reply tests."""

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.comments import (
    MetaInstagramPrivateCommentReplyProvider,
    MetaInstagramPrivateReplyErrorMapper,
    MetaInstagramPrivateReplyPayloadMapper,
    MetaInstagramPrivateReplyResponseParser,
    MetaInstagramPublicCommentReplyProvider,
    MetaInstagramPublicReplyErrorMapper,
    MetaInstagramPublicReplyResponseParser,
)
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_reply_executor(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaRequestExecutor:
    """Build shared Meta HTTP infrastructure for reply tests."""

    return MetaRequestExecutor(
        request_builder=MetaRequestBuilder(
            MetaApiConfig(api_version="v24.0"),
            FakeInstagramAccessTokenProvider({connection_id: "token"}),
        ),
        transport=transport,
        decoder=MetaResponseDecoder(MetaErrorDecoder()),
        retry_policy=MetaRetryPolicy(base_delay_seconds=0),
        observer=NullMetaHttpObserver(),
    )


def build_public_reply_provider(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramPublicCommentReplyProvider:
    """Build the Stage 8 Meta public reply provider."""

    return MetaInstagramPublicCommentReplyProvider(
        build_reply_executor(transport, connection_id),
        MetaInstagramPublicReplyResponseParser(),
        MetaInstagramPublicReplyErrorMapper(),
    )


def build_private_reply_provider(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramPrivateCommentReplyProvider:
    """Build the Stage 8 Meta private reply provider."""

    return MetaInstagramPrivateCommentReplyProvider(
        build_reply_executor(transport, connection_id),
        MetaInstagramPrivateReplyPayloadMapper(),
        MetaInstagramPrivateReplyResponseParser(),
        MetaInstagramPrivateReplyErrorMapper(),
    )
