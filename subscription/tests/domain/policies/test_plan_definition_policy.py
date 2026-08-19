import pytest

from subscription import BooleanEntitlementValue, EntitlementKey, PlanDefinitionPolicy, PlanEntitlement
from tests.support.domain.plan_builder import PlanBuilder


def test_plan_definition_policy_accepts_valid_plan() -> None:
    PlanDefinitionPolicy().validate(PlanBuilder().build())


@pytest.mark.parametrize("name", ["", " Pro", "Pro ", "x" * 121])
def test_plan_definition_policy_rejects_invalid_name(name: str) -> None:
    with pytest.raises(ValueError, match="plan name"):
        PlanDefinitionPolicy().validate(PlanBuilder().with_name(name).build())


def test_plan_definition_policy_rejects_untrimmed_description() -> None:
    with pytest.raises(ValueError, match="description"):
        PlanDefinitionPolicy().validate(PlanBuilder().with_description(" Pro plan ").build())


def test_plan_definition_policy_rejects_duplicate_entitlement_keys() -> None:
    first = PlanEntitlement(EntitlementKey("analytics.advanced"), BooleanEntitlementValue(True))
    second = PlanEntitlement(EntitlementKey("analytics.advanced"), BooleanEntitlementValue(False))

    with pytest.raises(ValueError, match="unique"):
        PlanDefinitionPolicy().validate(PlanBuilder().with_entitlements(first, second).build())
