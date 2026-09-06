"""Timestamp unit normalization for Meta Instagram webhooks."""

MILLISECONDS_EPOCH_THRESHOLD = 10_000_000_000


def normalize_meta_webhook_epoch_seconds(value: int) -> float:
    """Normalize Meta epoch timestamps expressed in seconds or milliseconds."""

    if abs(value) >= MILLISECONDS_EPOCH_THRESHOLD:
        return value / 1000
    return float(value)
