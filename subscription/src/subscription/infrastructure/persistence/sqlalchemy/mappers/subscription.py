from datetime import timedelta
from uuid import UUID

from subscription.domain import (
    SubjectReference,
    Subscription,
    SubscriptionSource,
    SubscriptionStatus,
    SubscriptionType,
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
    UsageCondition,
    UsageMetric,
    UsagePeriod,
)
from subscription.infrastructure.persistence.sqlalchemy.models import (
    SubscriptionModel,
    TrialPolicyModel,
    TrialUsageConditionModel,
)


class SubscriptionPersistenceMapper:
    def to_model(self, subscription: Subscription) -> SubscriptionModel:
        return SubscriptionModel(
            id=str(subscription.id),
            subject_type=subscription.subject.subject_type,
            subject_id=subscription.subject.subject_id,
            plan_id=str(subscription.plan_id),
            subscription_type=subscription.subscription_type.value,
            source=subscription.source.value,
            status=subscription.status.value,
            created_at=subscription.created_at,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at,
            trial_started_at=subscription.trial_started_at,
            cancelled_at=subscription.cancelled_at,
            expired_at=subscription.expired_at,
        )

    def trial_models(
        self,
        subscription: Subscription,
    ) -> tuple[TrialPolicyModel | None, tuple[TrialUsageConditionModel, ...]]:
        policy = subscription.trial_policy
        if policy is None:
            return None, ()
        policy_model = TrialPolicyModel(
            subscription_id=str(subscription.id),
            completion_mode=policy.completion_mode.value,
            max_duration_seconds=(
                int(policy.time_condition.max_duration.total_seconds())
                if policy.time_condition is not None
                else None
            ),
        )
        usage_models = tuple(
            TrialUsageConditionModel(
                subscription_id=str(subscription.id),
                metric=condition.metric.key,
                period=condition.period.value,
                limit=condition.limit,
            )
            for condition in policy.usage_conditions
        )
        return policy_model, usage_models

    def to_domain(
        self,
        model: SubscriptionModel,
        trial_model: TrialPolicyModel | None,
        usage_models: tuple[TrialUsageConditionModel, ...],
    ) -> Subscription:
        trial_policy = None
        if trial_model is not None:
            seconds = trial_model.max_duration_seconds
            trial_policy = TrialPolicy(
                completion_mode=TrialCompletionMode(trial_model.completion_mode),
                time_condition=TimeCondition(timedelta(seconds=seconds)) if seconds is not None else None,
                usage_conditions=tuple(
                    UsageCondition(
                        metric=UsageMetric(item.metric),
                        limit=item.limit,
                        period=UsagePeriod(item.period),
                    )
                    for item in usage_models
                ),
            )
        return Subscription(
            id=UUID(model.id),
            subject=SubjectReference(model.subject_type, model.subject_id),
            plan_id=UUID(model.plan_id),
            subscription_type=SubscriptionType(model.subscription_type),
            source=SubscriptionSource(model.source),
            status=SubscriptionStatus(model.status),
            created_at=model.created_at,
            started_at=model.started_at,
            expires_at=model.expires_at,
            trial_policy=trial_policy,
            trial_started_at=model.trial_started_at,
            cancelled_at=model.cancelled_at,
            expired_at=model.expired_at,
        )
