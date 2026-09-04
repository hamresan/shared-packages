"""Factories for Meta outbound messaging tests."""

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from instagram_api.infrastructure.meta.messaging import (
    MetaInstagramMessageRecipientEligibilityChecker,
    MetaInstagramMessageSendErrorMapper,
    MetaInstagramMessageSendResponseParser,
    MetaInstagramMessagingFieldParser,
    MetaInstagramMessagingPayloadParser,
    MetaInstagramOutboundMessageProvider,
    MetaInstagramOutboundPayloadMapper,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_outbound_executor(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaRequestExecutor:
    """Build the shared Meta executor used by outbound messaging tests."""

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


def build_outbound_provider(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramOutboundMessageProvider:
    """Build the Stage 6 Send API provider."""

    return MetaInstagramOutboundMessageProvider(
        build_outbound_executor(transport, connection_id),
        MetaInstagramOutboundPayloadMapper(),
        MetaInstagramMessageSendResponseParser(),
        MetaInstagramMessageSendErrorMapper(),
    )


def build_eligibility_checker(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramMessageRecipientEligibilityChecker:
    """Build the Stage 6 recipient eligibility checker."""

    return MetaInstagramMessageRecipientEligibilityChecker(
        build_outbound_executor(transport, connection_id),
        MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser()),
    )
