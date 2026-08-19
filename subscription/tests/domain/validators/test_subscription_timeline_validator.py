from datetime import UTC, datetime

import pytest

from subscription import (
    SubscriptionTimelineValidator,
    TimestampOrderValidator,
    TimezoneAwareDatetimeValidator,
)
from tests.support.domain.subscription_builder import SubscriptionBuilder


def build_timeline_validator() -> SubscriptionTimelineValidator:
    return SubscriptionTimelineValidator(
        datetime_validator=TimezoneAwareDatetimeValidator(),
        timestamp_order_validator=TimestampOrderValidator(),
    )


def test_timeline_validator_rejects_naive_timestamp() -> None:
    subscription = SubscriptionBuilder().with_created_at(datetime(2026, 8, 19)).build()

    with pytest.raises(ValueError, match="created_at"):
        build_timeline_validator().validate(subscription)


def test_timeline_validator_rejects_start_before_creation() -> None:
    created_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    started_at = datetime(2026, 8, 18, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_created_at(created_at)
        .with_started_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="started_at"):
        build_timeline_validator().validate(subscription)


def test_timeline_validator_rejects_expiration_not_after_start() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_started_at(started_at)
        .with_expires_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="expires_at"):
        build_timeline_validator().validate(subscription)
