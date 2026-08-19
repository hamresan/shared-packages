from datetime import UTC, datetime

import pytest

from subscription import TimestampOrderValidator


def test_timestamp_order_validator_accepts_forward_order() -> None:
    earlier = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    later = datetime(2026, 8, 20, 9, 0, tzinfo=UTC)

    TimestampOrderValidator().ensure_not_before(later, earlier, "later", "earlier")
    TimestampOrderValidator().ensure_after(later, earlier, "later", "earlier")


def test_timestamp_order_validator_rejects_value_before_minimum() -> None:
    earlier = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    later = datetime(2026, 8, 20, 9, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="must not be before"):
        TimestampOrderValidator().ensure_not_before(earlier, later, "earlier", "later")


def test_timestamp_order_validator_rejects_non_strict_after_order() -> None:
    value = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="must be after"):
        TimestampOrderValidator().ensure_after(value, value, "value", "minimum")
