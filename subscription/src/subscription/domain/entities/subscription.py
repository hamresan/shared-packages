from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from subscription.domain.entities.trial_policy import TrialPolicy
from subscription.domain.enums.subscription import (
    SubscriptionSource,
    SubscriptionStatus,
    SubscriptionType,
)
from subscription.domain.value_objects.subject_reference import SubjectReference


@dataclass(frozen=True, slots=True)
class Subscription:
    """Immutable snapshot of one subject's subscription lifecycle state."""

    id: UUID
    subject: SubjectReference
    plan_id: UUID
    subscription_type: SubscriptionType
    source: SubscriptionSource
    status: SubscriptionStatus
    created_at: datetime
    started_at: datetime | None = None
    expires_at: datetime | None = None
    trial_policy: TrialPolicy | None = None
    trial_started_at: datetime | None = None
    cancelled_at: datetime | None = None
    expired_at: datetime | None = None
