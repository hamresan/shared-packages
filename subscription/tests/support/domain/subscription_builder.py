from datetime import UTC, datetime
from uuid import UUID

from subscription import (
    SubjectReference,
    Subscription,
    SubscriptionSource,
    SubscriptionStatus,
    SubscriptionType,
    TrialPolicy,
)


class SubscriptionBuilder:
    def __init__(self) -> None:
        self._id = UUID("22222222-2222-2222-2222-222222222222")
        self._subject = SubjectReference("store", "store-1")
        self._plan_id = UUID("11111111-1111-1111-1111-111111111111")
        self._subscription_type = SubscriptionType.BASE
        self._source = SubscriptionSource.MANUAL
        self._status = SubscriptionStatus.PENDING
        self._created_at = datetime(2026, 7, 1, 8, 0, tzinfo=UTC)
        self._started_at: datetime | None = None
        self._expires_at: datetime | None = None
        self._trial_policy: TrialPolicy | None = None
        self._trial_started_at: datetime | None = None
        self._cancelled_at: datetime | None = None
        self._expired_at: datetime | None = None

    def with_id(self, subscription_id: UUID) -> "SubscriptionBuilder":
        self._id = subscription_id
        return self

    def with_subject(self, subject: SubjectReference) -> "SubscriptionBuilder":
        self._subject = subject
        return self

    def with_subscription_type(self, subscription_type: SubscriptionType) -> "SubscriptionBuilder":
        self._subscription_type = subscription_type
        return self

    def with_source(self, source: SubscriptionSource) -> "SubscriptionBuilder":
        self._source = source
        return self

    def with_status(self, status: SubscriptionStatus) -> "SubscriptionBuilder":
        self._status = status
        return self

    def with_created_at(self, created_at: datetime) -> "SubscriptionBuilder":
        self._created_at = created_at
        return self

    def with_started_at(self, started_at: datetime | None) -> "SubscriptionBuilder":
        self._started_at = started_at
        return self

    def with_expires_at(self, expires_at: datetime | None) -> "SubscriptionBuilder":
        self._expires_at = expires_at
        return self

    def with_trial_policy(self, trial_policy: TrialPolicy | None) -> "SubscriptionBuilder":
        self._trial_policy = trial_policy
        return self

    def with_trial_started_at(self, trial_started_at: datetime | None) -> "SubscriptionBuilder":
        self._trial_started_at = trial_started_at
        return self

    def with_cancelled_at(self, cancelled_at: datetime | None) -> "SubscriptionBuilder":
        self._cancelled_at = cancelled_at
        return self

    def with_expired_at(self, expired_at: datetime | None) -> "SubscriptionBuilder":
        self._expired_at = expired_at
        return self

    def build(self) -> Subscription:
        return Subscription(
            id=self._id,
            subject=self._subject,
            plan_id=self._plan_id,
            subscription_type=self._subscription_type,
            source=self._source,
            status=self._status,
            created_at=self._created_at,
            started_at=self._started_at,
            expires_at=self._expires_at,
            trial_policy=self._trial_policy,
            trial_started_at=self._trial_started_at,
            cancelled_at=self._cancelled_at,
            expired_at=self._expired_at,
        )
