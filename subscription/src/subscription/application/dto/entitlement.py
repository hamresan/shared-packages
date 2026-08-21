from dataclasses import dataclass
from uuid import UUID

from subscription.domain import EntitlementValue


@dataclass(frozen=True, slots=True)
class EntitlementGrant:
    subscription_id: UUID
    plan_id: UUID
    value: EntitlementValue
