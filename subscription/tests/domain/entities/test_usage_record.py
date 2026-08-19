from datetime import UTC, datetime

import pytest

from subscription import SubjectReference, UsageMetric, UsageRecord


def test_usage_record_accepts_positive_usage_event() -> None:
    record = UsageRecord(
        subject=SubjectReference("store", "store-1"),
        metric=UsageMetric("conversations"),
        amount=2,
        occurred_at=datetime(2026, 8, 19, tzinfo=UTC),
    )

    assert record.amount == 2


@pytest.mark.parametrize("amount", [0, -1, True])
def test_usage_record_rejects_invalid_amount(amount: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        UsageRecord(
            subject=SubjectReference("store", "store-1"),
            metric=UsageMetric("conversations"),
            amount=amount,
            occurred_at=datetime(2026, 8, 19, tzinfo=UTC),
        )


def test_usage_record_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        UsageRecord(
            subject=SubjectReference("store", "store-1"),
            metric=UsageMetric("conversations"),
            amount=1,
            occurred_at=datetime(2026, 8, 19),
        )
