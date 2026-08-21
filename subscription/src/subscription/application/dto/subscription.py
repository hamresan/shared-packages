from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from subscription.domain import SubjectReference, SubscriptionSource, TrialPolicy


@dataclass(frozen=True, slots=True)
class CreateSubscriptionCommand:
    subject: SubjectReference
    plan_id: UUID
    source: SubscriptionSource
    trial_policy: TrialPolicy | None = None


@dataclass(frozen=True, slots=True)
class ActivateSubscriptionCommand:
    subscription_id: UUID
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RenewSubscriptionCommand:
    subscription_id: UUID
    new_expires_at: datetime
