from decimal import Decimal

from subscription import (
    BooleanEntitlementValue,
    DecimalEntitlementValue,
    EntitlementKey,
    PlanEntitlement,
)
from subscription.infrastructure.persistence.sqlalchemy.mappers import (
    EntitlementPersistenceMapper,
    PlanPersistenceMapper,
)
from tests.support.domain.plan_builder import PlanBuilder


def test_plan_mapper_round_trips_typed_entitlements() -> None:
    plan = (
        PlanBuilder()
        .with_entitlements(
            PlanEntitlement(EntitlementKey("feature.enabled"), BooleanEntitlementValue(True)),
            PlanEntitlement(
                EntitlementKey("credits.max"),
                DecimalEntitlementValue(Decimal("12.5")),
            ),
        )
        .build()
    )
    mapper = PlanPersistenceMapper(EntitlementPersistenceMapper())

    model = mapper.to_model(plan)
    entitlement_models = mapper.entitlement_models(plan)
    result = mapper.to_domain(model, entitlement_models)

    assert result == plan
