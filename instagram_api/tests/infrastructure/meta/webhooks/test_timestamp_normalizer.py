"""Meta Instagram webhook timestamp normalization tests."""

from instagram_api.infrastructure.meta.webhooks import (
    normalize_meta_webhook_epoch_seconds,
)


def test_preserves_epoch_seconds() -> None:
    assert normalize_meta_webhook_epoch_seconds(1788523200) == 1788523200.0


def test_converts_epoch_milliseconds_to_seconds() -> None:
    assert normalize_meta_webhook_epoch_seconds(1788523200000) == 1788523200.0
