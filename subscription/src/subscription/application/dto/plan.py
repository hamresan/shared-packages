from dataclasses import dataclass

from subscription.domain import EntitlementValue, PlanStatus, SubscriptionType


@dataclass(frozen=True, slots=True)
class PlanEntitlementInput:
    key: str
    value: EntitlementValue


@dataclass(frozen=True, slots=True)
class CreatePlanCommand:
    code: str
    name: str
    subscription_type: SubscriptionType
    entitlements: tuple[PlanEntitlementInput, ...] = ()
    description: str | None = None
    status: PlanStatus = PlanStatus.ACTIVE
