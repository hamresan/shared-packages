"""Factories for Meta Instagram webhook tests."""

from instagram_api.infrastructure.meta.webhooks import (
    MetaInstagramCommentWebhookFieldParser,
    MetaInstagramCommentWebhookMapper,
    MetaInstagramCommentWebhookPayloadParser,
    MetaInstagramMessageWebhookMapper,
    MetaInstagramMessagingMetadataMapper,
    MetaInstagramMessagingWebhookFieldParser,
    MetaInstagramMessagingWebhookMapper,
    MetaInstagramWebhookEventIdFactory,
    MetaInstagramWebhookEventMapper,
    MetaInstagramWebhookFieldParser,
    MetaInstagramWebhookParser,
)


def build_meta_webhook_parser() -> MetaInstagramWebhookParser:
    """Build the real Meta webhook parser with current normalization layers."""

    messaging_fields = MetaInstagramMessagingWebhookFieldParser()
    comment_fields = MetaInstagramCommentWebhookFieldParser()
    return MetaInstagramWebhookParser(
        MetaInstagramWebhookFieldParser(),
        MetaInstagramWebhookEventMapper(MetaInstagramWebhookEventIdFactory()),
        MetaInstagramMessagingWebhookMapper(
            messaging_fields,
            MetaInstagramMessageWebhookMapper(messaging_fields),
            MetaInstagramMessagingMetadataMapper(messaging_fields),
        ),
        MetaInstagramCommentWebhookPayloadParser(comment_fields),
        MetaInstagramCommentWebhookMapper(),
    )
