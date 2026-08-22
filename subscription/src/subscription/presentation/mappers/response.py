from subscription.application import EntitlementGrant
from subscription.domain import Plan, Subscription, UsageCounter, UsageRecord
from subscription.presentation.mappers.entitlement_value import EntitlementValuePresentationMapper
from subscription.presentation.schemas.common import SubjectReferenceSchema
from subscription.presentation.schemas.entitlement import (
    EntitlementGrantResponse,
    EntitlementResponse,
)
from subscription.presentation.schemas.plan import PlanEntitlementResponse, PlanResponse
from subscription.presentation.schemas.subscription import SubscriptionResponse
from subscription.presentation.schemas.usage import UsageCounterResponse, UsageRecordResponse


class SubscriptionResponseMapper:
    def __init__(self, entitlement_value_mapper: EntitlementValuePresentationMapper) -> None:
        self._entitlement_value_mapper = entitlement_value_mapper

    def plan(self, plan: Plan) -> PlanResponse:
        return PlanResponse(
            id=plan.id,
            code=plan.code.value,
            name=plan.name,
            description=plan.description,
            subscription_type=plan.subscription_type,
            status=plan.status,
            entitlements=[
                PlanEntitlementResponse(
                    key=item.key.value,
                    value=self._entitlement_value_mapper.to_schema(item.value),
                )
                for item in plan.entitlements
            ],
        )

    def subscription(self, subscription: Subscription) -> SubscriptionResponse:
        return SubscriptionResponse(
            id=subscription.id,
            subject=SubjectReferenceSchema(
                subject_type=subscription.subject.subject_type,
                subject_id=subscription.subject.subject_id,
            ),
            plan_id=subscription.plan_id,
            subscription_type=subscription.subscription_type,
            source=subscription.source,
            status=subscription.status,
            created_at=subscription.created_at,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at,
            trial_started_at=subscription.trial_started_at,
            cancelled_at=subscription.cancelled_at,
            expired_at=subscription.expired_at,
        )

    def usage_record(self, record: UsageRecord) -> UsageRecordResponse:
        return UsageRecordResponse(
            subject=SubjectReferenceSchema(
                subject_type=record.subject.subject_type,
                subject_id=record.subject.subject_id,
            ),
            metric=record.metric.key,
            amount=record.amount,
            occurred_at=record.occurred_at,
        )

    def usage_counter(self, counter: UsageCounter) -> UsageCounterResponse:
        return UsageCounterResponse(
            metric=counter.metric.key,
            period=counter.period,
            consumed=counter.consumed,
        )

    def entitlements(self, grants: tuple[EntitlementGrant, ...]) -> EntitlementResponse:
        return EntitlementResponse(
            grants=[
                EntitlementGrantResponse(
                    subscription_id=grant.subscription_id,
                    plan_id=grant.plan_id,
                    value=self._entitlement_value_mapper.to_schema(grant.value),
                )
                for grant in grants
            ]
        )
