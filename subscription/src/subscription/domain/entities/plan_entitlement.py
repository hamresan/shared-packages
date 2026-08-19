from dataclasses import dataclass

from subscription.domain.value_objects.entitlement_key import EntitlementKey
from subscription.domain.value_objects.entitlement_values import EntitlementValue


@dataclass(frozen=True, slots=True)
class PlanEntitlement:
    key: EntitlementKey
    value: EntitlementValue
