from dataclasses import dataclass
from uuid import UUID

from subscription.domain.entities.plan_entitlement import PlanEntitlement
from subscription.domain.enums.plan import PlanStatus
from subscription.domain.enums.subscription import SubscriptionType
from subscription.domain.value_objects.plan_code import PlanCode


@dataclass(frozen=True, slots=True)
class Plan:
    id: UUID
    code: PlanCode
    name: str
    description: str | None
    subscription_type: SubscriptionType
    status: PlanStatus
    entitlements: tuple[PlanEntitlement, ...]
