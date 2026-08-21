from datetime import timedelta

import pytest

from subscription import EntitlementKey, SubscriptionStatus, SubscriptionValidityPolicy
from subscription.application import ResolveEntitlementsService
from subscription.domain import TimezoneAwareDatetimeValidator
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory, FixedClock
from tests.support.domain.plan_builder import PlanBuilder
from tests.support.domain.subscription_builder import SubscriptionBuilder


@pytest.mark.asyncio
async def test_resolve_entitlements_service_returns_grants_from_valid_subscriptions() -> None:
    clock = FixedClock()
    plan = PlanBuilder().build()
    subscription = (
        SubscriptionBuilder()
        .with_status(SubscriptionStatus.ACTIVE)
        .with_started_at(clock.now() - timedelta(days=1))
        .build()
    )
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(
        plans=(plan,),
        subscriptions=(subscription,),
    )
    service = ResolveEntitlementsService(
        unit_of_work_factory,
        clock,
        SubscriptionValidityPolicy(TimezoneAwareDatetimeValidator()),
    )

    result = await service.execute(
        subscription.subject,
        EntitlementKey("analytics.advanced"),
    )

    assert len(result) == 1
    assert result[0].subscription_id == subscription.id
    assert result[0].value == plan.entitlements[0].value


@pytest.mark.asyncio
async def test_resolve_entitlements_service_ignores_inactive_subscription() -> None:
    plan = PlanBuilder().build()
    subscription = SubscriptionBuilder().build()
    service = ResolveEntitlementsService(
        FakeSubscriptionUnitOfWorkFactory(
            plans=(plan,),
            subscriptions=(subscription,),
        ),
        FixedClock(),
        SubscriptionValidityPolicy(TimezoneAwareDatetimeValidator()),
    )

    assert await service.execute(
        subscription.subject,
        EntitlementKey("analytics.advanced"),
    ) == ()
