from datetime import timedelta

import pytest

from subscription import (
    SubscriptionStatus,
    TrialCompletionMode,
    TrialPolicy,
    UsageCondition,
    UsageMetric,
    UsagePeriod,
)
from subscription.application import EvaluateTrialService
from subscription.domain import TrialEvaluationPolicy
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory, FixedClock
from tests.support.domain.subscription_builder import SubscriptionBuilder


@pytest.mark.asyncio
async def test_evaluate_trial_service_loads_usage_counters() -> None:
    clock = FixedClock()
    metric = UsageMetric("conversations")
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        usage_conditions=(UsageCondition(metric, 100, UsagePeriod.TRIAL),),
    )
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(clock.now() - timedelta(days=1))
        .with_trial_policy(policy)
        .with_trial_started_at(clock.now() - timedelta(days=1))
        .build()
    )
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    unit_of_work_factory.usage_repository.counters[
        (subscription.subject, metric, UsagePeriod.TRIAL)
    ] = 100
    service = EvaluateTrialService(
        unit_of_work_factory,
        clock,
        TrialEvaluationPolicy(),
    )

    assert await service.execute(subscription.id) is True


@pytest.mark.asyncio
async def test_evaluate_trial_service_returns_false_without_trial_state() -> None:
    subscription = SubscriptionBuilder().build()
    service = EvaluateTrialService(
        FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,)),
        FixedClock(),
        TrialEvaluationPolicy(),
    )

    assert await service.execute(subscription.id) is False
