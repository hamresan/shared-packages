from uuid import UUID

import pytest

from subscription import BooleanEntitlementValue, PlanDefinitionPolicy, SubscriptionType
from subscription.application import CreatePlanCommand, CreatePlanMapper, PlanEntitlementInput
from tests.support.application.fakes import FixedIdentifierGenerator


def test_create_plan_mapper_builds_valid_plan() -> None:
    plan_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    mapper = CreatePlanMapper(FixedIdentifierGenerator(plan_id), PlanDefinitionPolicy())

    plan = mapper.map(
        CreatePlanCommand(
            code="pro",
            name="Pro",
            subscription_type=SubscriptionType.BASE,
            entitlements=(
                PlanEntitlementInput("analytics.advanced", BooleanEntitlementValue(True)),
            ),
        )
    )

    assert plan.id == plan_id
    assert plan.code.value == "pro"
    assert plan.entitlements[0].key.value == "analytics.advanced"


def test_create_plan_mapper_applies_domain_validation() -> None:
    mapper = CreatePlanMapper(
        FixedIdentifierGenerator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")),
        PlanDefinitionPolicy(),
    )

    with pytest.raises(ValueError, match="name"):
        mapper.map(
            CreatePlanCommand(
                code="pro",
                name=" Pro ",
                subscription_type=SubscriptionType.BASE,
            )
        )
