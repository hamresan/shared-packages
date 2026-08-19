from datetime import UTC, datetime, timedelta

import pytest

from subscription import (
    SubscriptionDefinitionPolicy,
    SubscriptionStatus,
    TimeCondition,
    TimezoneAwareDatetimeValidator,
    TrialCompletionMode,
    TrialPolicy,
)
from tests.support.domain.subscription_builder import SubscriptionBuilder


def build_policy() -> SubscriptionDefinitionPolicy:
    return SubscriptionDefinitionPolicy(TimezoneAwareDatetimeValidator())


def test_subscription_definition_policy_accepts_pending_subscription() -> None:
    build_policy().validate(SubscriptionBuilder().build())


def test_subscription_definition_policy_rejects_naive_timestamp() -> None:
    subscription = SubscriptionBuilder().with_created_at(datetime(2026, 8, 19)).build()

    with pytest.raises(ValueError, match="created_at"):
        build_policy().validate(subscription)


def test_subscription_definition_policy_requires_started_at_for_active_subscription() -> None:
    subscription = SubscriptionBuilder().with_status(SubscriptionStatus.ACTIVE).build()

    with pytest.raises(ValueError, match="requires started_at"):
        build_policy().validate(subscription)


def test_subscription_definition_policy_requires_trial_state_for_trialing_subscription() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="trial_policy"):
        build_policy().validate(subscription)


def test_subscription_definition_policy_accepts_valid_trialing_subscription() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    trial_policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
    )
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(started_at)
        .with_trial_policy(trial_policy)
        .with_trial_started_at(started_at)
        .build()
    )

    build_policy().validate(subscription)


def test_subscription_definition_policy_rejects_expiration_before_start() -> None:
    started_at = datetime(2026, 8, 20, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .with_expires_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="expires_at"):
        build_policy().validate(subscription)


def test_subscription_definition_policy_requires_cancellation_timestamp() -> None:
    subscription = SubscriptionBuilder().with_status(SubscriptionStatus.CANCELLED).build()

    with pytest.raises(ValueError, match="cancelled_at"):
        build_policy().validate(subscription)


def test_subscription_definition_policy_requires_expiration_timestamp() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.EXPIRED)
        .with_started_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="expired_at"):
        build_policy().validate(subscription)
