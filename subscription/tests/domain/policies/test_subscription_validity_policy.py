from datetime import UTC, datetime, timedelta

from subscription import SubscriptionStatus, SubscriptionValidityPolicy, TimezoneAwareDatetimeValidator
from tests.support.domain.subscription_builder import SubscriptionBuilder


def build_policy() -> SubscriptionValidityPolicy:
    return SubscriptionValidityPolicy(TimezoneAwareDatetimeValidator())


def test_active_subscription_is_valid_inside_its_term() -> None:
    started_at = datetime(2026, 8, 19, 8, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .with_expires_at(started_at + timedelta(days=30))
        .build()
    )

    assert build_policy().is_valid(subscription, started_at + timedelta(days=1))


def test_active_subscription_is_invalid_at_expiration_boundary() -> None:
    started_at = datetime(2026, 8, 19, 8, 0, tzinfo=UTC)
    expires_at = started_at + timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .with_expires_at(expires_at)
        .build()
    )

    assert not build_policy().is_valid(subscription, expires_at)


def test_pending_subscription_is_not_valid() -> None:
    subscription = SubscriptionBuilder().build()

    assert not build_policy().is_valid(subscription, datetime(2026, 8, 20, tzinfo=UTC))


def test_trialing_subscription_is_invalid_when_trial_is_complete() -> None:
    started_at = datetime(2026, 8, 19, 8, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(started_at)
        .build()
    )

    assert not build_policy().is_valid(
        subscription,
        started_at + timedelta(days=1),
        trial_completed=True,
    )
