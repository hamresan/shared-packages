from uuid import UUID

import pytest

from subscription.application import GetPlanService, PlanNotFoundError
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory
from tests.support.domain.plan_builder import PlanBuilder


@pytest.mark.asyncio
async def test_get_plan_service_returns_plan() -> None:
    plan = PlanBuilder().build()
    service = GetPlanService(FakeSubscriptionUnitOfWorkFactory(plans=(plan,)))

    assert await service.execute(plan.id) == plan


@pytest.mark.asyncio
async def test_get_plan_service_raises_when_missing() -> None:
    service = GetPlanService(FakeSubscriptionUnitOfWorkFactory())

    with pytest.raises(PlanNotFoundError):
        await service.execute(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
