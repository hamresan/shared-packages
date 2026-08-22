from uuid import UUID

import pytest

from subscription.application import GetSubscriptionService, SubscriptionNotFoundError
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory
from tests.support.domain.subscription_builder import SubscriptionBuilder

SUBSCRIPTION_ID = UUID("22222222-2222-2222-2222-222222222222")


async def test_get_subscription_returns_existing_subscription() -> None:
    subscription = SubscriptionBuilder().build()
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(subscriptions=(subscription,))
    service = GetSubscriptionService(unit_of_work_factory)

    result = await service.execute(subscription.id)

    assert result == subscription


async def test_get_subscription_raises_when_missing() -> None:
    service = GetSubscriptionService(FakeSubscriptionUnitOfWorkFactory())

    with pytest.raises(SubscriptionNotFoundError):
        await service.execute(SUBSCRIPTION_ID)
