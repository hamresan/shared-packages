from datetime import UTC, datetime, timedelta

import pytest

from subscription import (
    SubscriptionStateValidator,
    SubscriptionStatus,
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
)
from tests.support.domain.subscription_builder import SubscriptionBuilder


def test_state_validator_requires_started_at_for_active_subscription() -> None:
    subscription = SubscriptionBuilder().with_status(SubscriptionStatus.ACTIVE).build()

    with pytest.raises(ValueError, match="started_at"):
        SubscriptionStateValidator().validate(subscription)


def test_state_validator_requires_trial_state_for_trialing_subscription() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="trial_policy"):
        SubscriptionStateValidator().validate(subscription)


def test_state_validator_accepts_complete_trial_state() -> None:
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

    SubscriptionStateValidator().validate(subscription)


def test_state_validator_requires_cancellation_timestamp() -> None:
    subscription = SubscriptionBuilder().with_status(SubscriptionStatus.CANCELLED).build()

    with pytest.raises(ValueError, match="cancelled_at"):
        SubscriptionStateValidator().validate(subscription)


def test_state_validator_requires_expiration_timestamp() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.EXPIRED)
        .with_started_at(started_at)
        .build()
    )

    with pytest.raises(ValueError, match="expired_at"):
        SubscriptionStateValidator().validate(subscription)
