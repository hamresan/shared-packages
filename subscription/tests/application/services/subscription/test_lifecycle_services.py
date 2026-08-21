from dataclasses import replace
from datetime import timedelta
from uuid import UUID

import pytest

from subscription import (
    ActiveBaseSubscriptionPolicy,
    SubscriptionStatus,
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
)
from subscription.application import (
    ActivateSubscriptionCommand,
    ActivateSubscriptionService,
    CancelSubscriptionService,
    RenewSubscriptionCommand,
    RenewSubscriptionService,
    StartTrialService,
)
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory, FixedClock
from tests.support.domain.subscription_builder import SubscriptionBuilder
from tests.support.domain.subscription_lifecycle_factory import build_subscription_lifecycle_service


@pytest.mark.asyncio
async def test_activate_subscription_service_persists_active_snapshot() -> None:
    subscription = SubscriptionBuilder().build()
    clock = FixedClock()
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    service = ActivateSubscriptionService(
        unit_of_work_factory,
        clock,
        build_subscription_lifecycle_service(),
        ActiveBaseSubscriptionPolicy(),
    )

    result = await service.execute(ActivateSubscriptionCommand(subscription.id))

    assert result.status is SubscriptionStatus.ACTIVE
    assert result.started_at == clock.now()
    assert unit_of_work_factory.unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_activate_subscription_service_rejects_second_active_base() -> None:
    candidate = SubscriptionBuilder().build()
    existing = replace(
        SubscriptionBuilder().build(),
        id=UUID("33333333-3333-3333-3333-333333333333"),
        status=SubscriptionStatus.ACTIVE,
        started_at=FixedClock().now(),
    )
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(candidate, existing))
    service = ActivateSubscriptionService(
        unit_of_work_factory,
        FixedClock(),
        build_subscription_lifecycle_service(),
        ActiveBaseSubscriptionPolicy(),
    )

    with pytest.raises(ValueError, match="active BASE"):
        await service.execute(ActivateSubscriptionCommand(candidate.id))


@pytest.mark.asyncio
async def test_start_trial_service_starts_trial() -> None:
    trial_policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
    )
    subscription = SubscriptionBuilder().with_trial_policy(trial_policy).build()
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    service = StartTrialService(
        unit_of_work_factory,
        FixedClock(),
        build_subscription_lifecycle_service(),
        ActiveBaseSubscriptionPolicy(),
    )

    result = await service.execute(subscription.id)

    assert result.status is SubscriptionStatus.TRIALING
    assert result.trial_started_at == FixedClock().now()


@pytest.mark.asyncio
async def test_cancel_subscription_service_cancels_active_subscription() -> None:
    clock = FixedClock()
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(clock.now() - timedelta(days=1))
        .build()
    )
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    service = CancelSubscriptionService(
        unit_of_work_factory,
        clock,
        build_subscription_lifecycle_service(),
    )

    result = await service.execute(subscription.id)

    assert result.status is SubscriptionStatus.CANCELLED
    assert result.cancelled_at == clock.now()


@pytest.mark.asyncio
async def test_renew_subscription_service_reactivates_expired_subscription() -> None:
    clock = FixedClock()
    started_at = clock.now() - timedelta(days=30)
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.EXPIRED)
        .with_started_at(started_at)
        .with_expires_at(clock.now() - timedelta(days=1))
        .with_expired_at(clock.now() - timedelta(days=1))
        .build()
    )
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    service = RenewSubscriptionService(
        unit_of_work_factory,
        clock,
        build_subscription_lifecycle_service(),
        ActiveBaseSubscriptionPolicy(),
    )

    result = await service.execute(
        RenewSubscriptionCommand(
            subscription.id,
            clock.now() + timedelta(days=30),
        )
    )

    assert result.status is SubscriptionStatus.ACTIVE
    assert result.expired_at is None
