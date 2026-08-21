from uuid import UUID

import pytest

from subscription import PlanDefinitionPolicy, SubscriptionType
from subscription.application import (
    CreatePlanCommand,
    CreatePlanMapper,
    CreatePlanService,
    PlanCodeAlreadyExistsError,
)
from tests.support.application.fakes import (
    FakeSubscriptionUnitOfWorkFactory,
    FixedIdentifierGenerator,
)
from tests.support.domain.plan_builder import PlanBuilder


@pytest.mark.asyncio
async def test_create_plan_service_persists_and_commits() -> None:
    plan_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    service = CreatePlanService(
        unit_of_work_factory,
        CreatePlanMapper(FixedIdentifierGenerator(plan_id), PlanDefinitionPolicy()),
    )

    result = await service.execute(
        CreatePlanCommand(
            code="starter",
            name="Starter",
            subscription_type=SubscriptionType.BASE,
        )
    )

    assert unit_of_work_factory.plan_repository.items[plan_id] == result
    assert unit_of_work_factory.unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_create_plan_service_rejects_duplicate_code() -> None:
    existing = PlanBuilder().build()
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(plans=(existing,))
    service = CreatePlanService(
        unit_of_work_factory,
        CreatePlanMapper(
            FixedIdentifierGenerator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")),
            PlanDefinitionPolicy(),
        ),
    )

    with pytest.raises(PlanCodeAlreadyExistsError):
        await service.execute(
            CreatePlanCommand(
                code="pro",
                name="Another Pro",
                subscription_type=SubscriptionType.BASE,
            )
        )
