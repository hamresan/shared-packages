"""Factories for Meta messaging provider tests."""

from instagram_api.domain import InstagramConnectionId
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
from instagram_api.infrastructure.meta.messaging import (
    MetaInstagramConversationProvider,
    MetaInstagramMessageDetailAvailabilityPolicy,
    MetaInstagramMessageDetailReader,
    MetaInstagramMessageProvider,
    MetaInstagramMessageQueryBuilder,
    MetaInstagramMessagingFieldParser,
    MetaInstagramMessagingMapper,
    MetaInstagramMessagingPayloadParser,
    MetaInstagramMessagingTimestampParser,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_meta_executor(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaRequestExecutor:
    """Build the shared Meta executor used by messaging tests."""

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


def build_meta_message_detail_reader(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramMessageDetailReader:
    """Build a message-detail reader with real parsing and fake transport."""

    parser = MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser())
    return MetaInstagramMessageDetailReader(
        build_meta_executor(transport, connection_id),
        parser,
        MetaInstagramMessageDetailAvailabilityPolicy(),
    )


def build_meta_messaging_providers(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> tuple[MetaInstagramConversationProvider, MetaInstagramMessageProvider]:
    """Build Stage 5 providers with real shared infrastructure and fake transport."""

    parser = MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser())
    mapper = MetaInstagramMessagingMapper(MetaInstagramMessagingTimestampParser())
    executor = build_meta_executor(transport, connection_id)
    pagination_mapper = MetaPaginationCursorMapper()
    detail_reader = MetaInstagramMessageDetailReader(
        executor,
        parser,
        MetaInstagramMessageDetailAvailabilityPolicy(),
    )
    return (
        MetaInstagramConversationProvider(
            executor,
            parser,
            mapper,
            pagination_mapper,
        ),
        MetaInstagramMessageProvider(
            executor,
            parser,
            mapper,
            pagination_mapper,
            MetaInstagramMessageQueryBuilder(),
            detail_reader,
        ),
    )
