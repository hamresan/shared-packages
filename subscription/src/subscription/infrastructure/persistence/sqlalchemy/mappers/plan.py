from uuid import UUID

from subscription.domain import Plan, PlanCode, PlanStatus, SubscriptionType
from subscription.infrastructure.persistence.sqlalchemy.mappers.entitlement import (
    EntitlementPersistenceMapper,
)
from subscription.infrastructure.persistence.sqlalchemy.models import (
    PlanEntitlementModel,
    PlanModel,
)


class PlanPersistenceMapper:
    def __init__(self, entitlement_mapper: EntitlementPersistenceMapper) -> None:
        self._entitlement_mapper = entitlement_mapper

    def to_model(self, plan: Plan) -> PlanModel:
        return PlanModel(
            id=str(plan.id),
            code=plan.code.value,
            name=plan.name,
            description=plan.description,
            subscription_type=plan.subscription_type.value,
            status=plan.status.value,
        )

    def entitlement_models(self, plan: Plan) -> tuple[PlanEntitlementModel, ...]:
        plan_id = str(plan.id)
        return tuple(
            self._entitlement_mapper.to_model(plan_id, entitlement)
            for entitlement in plan.entitlements
        )

    def to_domain(
        self,
        model: PlanModel,
        entitlements: tuple[PlanEntitlementModel, ...],
    ) -> Plan:
        return Plan(
            id=UUID(model.id),
            code=PlanCode(model.code),
            name=model.name,
            description=model.description,
            subscription_type=SubscriptionType(model.subscription_type),
            status=PlanStatus(model.status),
            entitlements=tuple(self._entitlement_mapper.to_domain(item) for item in entitlements),
        )
