from datetime import UTC, datetime

from subscription import SubscriptionStatus
from tests.support.domain.subscription_builder import SubscriptionBuilder
from tests.support.domain.subscription_definition_validator_factory import (
    build_subscription_definition_validator,
)


def test_subscription_definition_validator_accepts_pending_subscription() -> None:
    build_subscription_definition_validator().validate(SubscriptionBuilder().build())


def test_subscription_definition_validator_accepts_active_subscription() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .build()
    )

    build_subscription_definition_validator().validate(subscription)
