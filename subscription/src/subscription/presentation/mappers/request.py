from datetime import timedelta
from uuid import UUID

from subscription.application import (
    ActivateSubscriptionCommand,
    CreatePlanCommand,
    CreateSubscriptionCommand,
    GetUsageCounterQuery,
    PlanEntitlementInput,
    RecordUsageCommand,
    RenewSubscriptionCommand,
)
from subscription.domain import SubjectReference, TimeCondition, TrialPolicy, UsageCondition, UsageMetric
from subscription.presentation.mappers.entitlement_value import EntitlementValuePresentationMapper
from subscription.presentation.schemas.common import SubjectReferenceSchema
from subscription.presentation.schemas.plan import CreatePlanRequest
from subscription.presentation.schemas.subscription import (
    ActivateSubscriptionRequest,
    CreateSubscriptionRequest,
    RenewSubscriptionRequest,
    TrialPolicyRequest,
)
from subscription.presentation.schemas.usage import RecordUsageRequest


class SubscriptionRequestMapper:
    def __init__(self, entitlement_value_mapper: EntitlementValuePresentationMapper) -> None:
        self._entitlement_value_mapper = entitlement_value_mapper

    def subject(self, schema: SubjectReferenceSchema) -> SubjectReference:
        return SubjectReference(schema.subject_type, schema.subject_id)

    def create_plan(self, request: CreatePlanRequest) -> CreatePlanCommand:
        entitlements = tuple(
            PlanEntitlementInput(
                key=item.key,
                value=self._entitlement_value_mapper.from_schema(item.value),
            )
            for item in request.entitlements
        )
        return CreatePlanCommand(
            code=request.code,
            name=request.name,
            description=request.description,
            subscription_type=request.subscription_type,
            status=request.status,
            entitlements=entitlements,
        )

    def create_subscription(self, request: CreateSubscriptionRequest) -> CreateSubscriptionCommand:
        return CreateSubscriptionCommand(
            subject=self.subject(request.subject),
            plan_id=request.plan_id,
            source=request.source,
            trial_policy=self.trial_policy(request.trial_policy),
        )

    def activate_subscription(
        self,
        subscription_id: UUID,
        request: ActivateSubscriptionRequest,
    ) -> ActivateSubscriptionCommand:
        return ActivateSubscriptionCommand(subscription_id, request.expires_at)

    def renew_subscription(
        self,
        subscription_id: UUID,
        request: RenewSubscriptionRequest,
    ) -> RenewSubscriptionCommand:
        return RenewSubscriptionCommand(subscription_id, request.new_expires_at)

    def record_usage(self, request: RecordUsageRequest) -> RecordUsageCommand:
        return RecordUsageCommand(
            subject=self.subject(request.subject),
            metric=UsageMetric(request.metric),
            amount=request.amount,
        )

    def usage_counter(
        self,
        subject: SubjectReference,
        metric: str,
        period: object,
    ) -> GetUsageCounterQuery:
        from subscription.domain import UsagePeriod

        if not isinstance(period, UsagePeriod):
            raise TypeError("period must be a UsagePeriod")
        return GetUsageCounterQuery(subject, UsageMetric(metric), period)

    def trial_policy(self, request: TrialPolicyRequest | None) -> TrialPolicy | None:
        if request is None:
            return None
        time_condition = (
            TimeCondition(timedelta(seconds=request.max_duration_seconds))
            if request.max_duration_seconds is not None
            else None
        )
        usage_conditions = tuple(
            UsageCondition(UsageMetric(item.metric), item.limit, item.period)
            for item in request.usage_conditions
        )
        return TrialPolicy(request.completion_mode, time_condition, usage_conditions)
