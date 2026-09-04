"""Factories for Meta Instagram comment tests."""

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.comments import (
    MetaInstagramCommentFieldParser,
    MetaInstagramCommentMapper,
    MetaInstagramCommentPayloadParser,
    MetaInstagramCommentProvider,
    MetaInstagramCommentTimestampParser,
)
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaPaginationCursorMapper,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_comment_provider(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramCommentProvider:
    """Build a Stage 7 Meta comment provider."""

    parser = MetaInstagramCommentPayloadParser(MetaInstagramCommentFieldParser())
    mapper = MetaInstagramCommentMapper(MetaInstagramCommentTimestampParser())
    executor = MetaRequestExecutor(
        request_builder=MetaRequestBuilder(
            MetaApiConfig(api_version="v24.0"),
            FakeInstagramAccessTokenProvider({connection_id: "token"}),
        ),
        transport=transport,
        decoder=MetaResponseDecoder(MetaErrorDecoder()),
        retry_policy=MetaRetryPolicy(base_delay_seconds=0),
        observer=NullMetaHttpObserver(),
    )
    return MetaInstagramCommentProvider(
        executor,
        parser,
        mapper,
        MetaPaginationCursorMapper(),
    )
