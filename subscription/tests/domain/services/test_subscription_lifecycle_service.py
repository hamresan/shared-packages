from datetime import UTC, datetime, timedelta

import pytest

from subscription import (
    SubscriptionStatus,
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
)
from tests.support.domain.subscription_builder import SubscriptionBuilder
from tests.support.domain.subscription_lifecycle_factory import build_subscription_lifecycle_service


def test_start_trial_creates_trialing_snapshot() -> None:
    at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    trial_policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
    )
    subscription = SubscriptionBuilder().with_trial_policy(trial_policy).build()

    result = build_subscription_lifecycle_service().start_trial(subscription, at)

    assert result.status is SubscriptionStatus.TRIALING
    assert result.started_at == at
    assert result.trial_started_at == at
    assert result.trial_policy is trial_policy


def test_start_trial_requires_trial_policy() -> None:
    with pytest.raises(ValueError, match="trial_policy"):
        build_subscription_lifecycle_service().start_trial(
            SubscriptionBuilder().build(),
            datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
        )


def test_activate_pending_subscription_sets_start_and_expiration() -> None:
    at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    expires_at = at + timedelta(days=30)

    result = build_subscription_lifecycle_service().activate(
        SubscriptionBuilder().build(),
        at,
        expires_at=expires_at,
    )

    assert result.status is SubscriptionStatus.ACTIVE
    assert result.started_at == at
    assert result.expires_at == expires_at


def test_activate_trialing_subscription_preserves_original_start() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    activated_at = started_at + timedelta(days=3)
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

    result = build_subscription_lifecycle_service().activate(subscription, activated_at)

    assert result.status is SubscriptionStatus.ACTIVE
    assert result.started_at == started_at
    assert result.trial_started_at == started_at


def test_cancel_active_subscription_sets_cancellation_timestamp() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    cancelled_at = started_at + timedelta(days=2)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .build()
    )

    result = build_subscription_lifecycle_service().cancel(subscription, cancelled_at)

    assert result.status is SubscriptionStatus.CANCELLED
    assert result.cancelled_at == cancelled_at


def test_expire_active_subscription_sets_expiration_timestamp() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    expired_at = started_at + timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .build()
    )

    result = build_subscription_lifecycle_service().expire(subscription, expired_at)

    assert result.status is SubscriptionStatus.EXPIRED
    assert result.expired_at == expired_at


def test_extend_active_subscription_moves_expiration_forward() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    current_expiration = started_at + timedelta(days=30)
    new_expiration = current_expiration + timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .with_expires_at(current_expiration)
        .build()
    )

    result = build_subscription_lifecycle_service().extend(subscription, new_expiration)

    assert result.expires_at == new_expiration


def test_extend_rejects_non_forward_expiration() -> None:
    started_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    current_expiration = started_at + timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(started_at)
        .with_expires_at(current_expiration)
        .build()
    )

    with pytest.raises(ValueError, match="after the current"):
        build_subscription_lifecycle_service().extend(subscription, current_expiration)


def test_renew_expired_subscription_reactivates_and_clears_expired_timestamp() -> None:
    started_at = datetime(2026, 7, 19, 9, 0, tzinfo=UTC)
    expired_at = datetime(2026, 8, 18, 9, 0, tzinfo=UTC)
    renewed_at = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    new_expiration = renewed_at + timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.EXPIRED)
        .with_started_at(started_at)
        .with_expires_at(expired_at)
        .with_expired_at(expired_at)
        .build()
    )

    result = build_subscription_lifecycle_service().renew(
        subscription,
        renewed_at,
        new_expiration,
    )

    assert result.status is SubscriptionStatus.ACTIVE
    assert result.expires_at == new_expiration
    assert result.expired_at is None


def test_cancelled_subscription_cannot_be_renewed() -> None:
    started_at = datetime(2026, 8, 10, 9, 0, tzinfo=UTC)
    cancelled_at = datetime(2026, 8, 18, 9, 0, tzinfo=UTC)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.CANCELLED)
        .with_started_at(started_at)
        .with_cancelled_at(cancelled_at)
        .build()
    )

    with pytest.raises(ValueError, match="not allowed"):
        build_subscription_lifecycle_service().renew(
            subscription,
            datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
            datetime(2026, 9, 19, 9, 0, tzinfo=UTC),
        )
