from uuid import UUID

from subscription import SubscriptionSource, SubscriptionStatus, SubjectReference
from subscription.application import CreateSubscriptionCommand, CreateSubscriptionMapper
from tests.support.application.fakes import FixedClock, FixedIdentifierGenerator
from tests.support.domain.plan_builder import PlanBuilder


def test_create_subscription_mapper_uses_plan_type_and_runtime_dependencies() -> None:
    subscription_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    clock = FixedClock()
    mapper = CreateSubscriptionMapper(FixedIdentifierGenerator(subscription_id), clock)
    plan = PlanBuilder().build()

    result = mapper.map(
        CreateSubscriptionCommand(
            subject=SubjectReference("store", "store-1"),
            plan_id=plan.id,
            source=SubscriptionSource.MANUAL,
        ),
        plan,
    )

    assert result.id == subscription_id
    assert result.subscription_type == plan.subscription_type
    assert result.status is SubscriptionStatus.PENDING
    assert result.created_at == clock.now()
