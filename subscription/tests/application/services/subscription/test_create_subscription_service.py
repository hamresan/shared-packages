from dataclasses import replace
from uuid import UUID

import pytest

from subscription import PlanStatus, SubscriptionSource, SubjectReference
from subscription.application import (
    CreateSubscriptionCommand,
    CreateSubscriptionMapper,
    CreateSubscriptionService,
    PlanNotFoundError,
    PlanUnavailableError,
)
from tests.support.application.fakes import (
    FakeSubscriptionUnitOfWorkFactory,
    FixedClock,
    FixedIdentifierGenerator,
)
from tests.support.domain.plan_builder import PlanBuilder


@pytest.mark.asyncio
async def test_create_subscription_service_uses_active_plan() -> None:
    plan = PlanBuilder().build()
    subscription_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory(plans=(plan,))
    service = CreateSubscriptionService(
        unit_of_work_factory,
        CreateSubscriptionMapper(
            FixedIdentifierGenerator(subscription_id),
            FixedClock(),
        ),
    )

    result = await service.execute(
        CreateSubscriptionCommand(
            subject=SubjectReference("store", "store-1"),
            plan_id=plan.id,
            source=SubscriptionSource.MANUAL,
        )
    )

    assert result.id == subscription_id
    assert unit_of_work_factory.subscription_repository.items[subscription_id] == result
    assert unit_of_work_factory.unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_create_subscription_service_rejects_missing_plan() -> None:
    service = CreateSubscriptionService(
        FakeSubscriptionUnitOfWorkFactory(),
        CreateSubscriptionMapper(
            FixedIdentifierGenerator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")),
            FixedClock(),
        ),
    )

    with pytest.raises(PlanNotFoundError):
        await service.execute(
            CreateSubscriptionCommand(
                subject=SubjectReference("store", "store-1"),
                plan_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                source=SubscriptionSource.MANUAL,
            )
        )


@pytest.mark.asyncio
async def test_create_subscription_service_rejects_inactive_plan() -> None:
    plan = replace(PlanBuilder().build(), status=PlanStatus.INACTIVE)
    service = CreateSubscriptionService(
        FakeSubscriptionUnitOfWorkFactory(plans=(plan,)),
        CreateSubscriptionMapper(
            FixedIdentifierGenerator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")),
            FixedClock(),
        ),
    )

    with pytest.raises(PlanUnavailableError):
        await service.execute(
            CreateSubscriptionCommand(
                subject=SubjectReference("store", "store-1"),
                plan_id=plan.id,
                source=SubscriptionSource.MANUAL,
            )
        )
