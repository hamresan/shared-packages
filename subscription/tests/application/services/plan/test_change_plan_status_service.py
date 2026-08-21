from dataclasses import replace

import pytest

from subscription import PlanStatus, PlanStatusTransitionPolicy
from subscription.application import ChangePlanStatusService
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory
from tests.support.domain.plan_builder import PlanBuilder


@pytest.mark.asyncio
async def test_change_plan_status_service_updates_plan() -> None:
    plan = replace(PlanBuilder().build(), status=PlanStatus.INACTIVE)
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(plans=(plan,))
    service = ChangePlanStatusService(
        unit_of_work_factory,
        PlanStatusTransitionPolicy(),
    )

    result = await service.execute(plan.id, PlanStatus.ACTIVE)

    assert result.status is PlanStatus.ACTIVE
    assert unit_of_work_factory.unit_of_work.commit_count == 1
