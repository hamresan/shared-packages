"""Factories for Meta Instagram webhook tests."""

from instagram_api.infrastructure.meta.webhooks import (
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
    """Build the real Meta webhook parser with Stage 10 messaging normalization."""

    messaging_fields = MetaInstagramMessagingWebhookFieldParser()
    return MetaInstagramWebhookParser(
        MetaInstagramWebhookFieldParser(),
        MetaInstagramWebhookEventMapper(MetaInstagramWebhookEventIdFactory()),
        MetaInstagramMessagingWebhookMapper(
            messaging_fields,
            MetaInstagramMessageWebhookMapper(messaging_fields),
            MetaInstagramMessagingMetadataMapper(messaging_fields),
        ),
    )
