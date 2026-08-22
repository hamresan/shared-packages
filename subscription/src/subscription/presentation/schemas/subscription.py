from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from subscription.domain import (
    SubscriptionSource,
    SubscriptionStatus,
    SubscriptionType,
    TrialCompletionMode,
)
from subscription.presentation.schemas.common import SubjectReferenceSchema, UsageConditionSchema


class TrialPolicyRequest(BaseModel):
    completion_mode: TrialCompletionMode
    max_duration_seconds: int | None = Field(default=None, gt=0)
    usage_conditions: list[UsageConditionSchema] = Field(default_factory=list)


class CreateSubscriptionRequest(BaseModel):
    subject: SubjectReferenceSchema
    plan_id: UUID
    source: SubscriptionSource
    trial_policy: TrialPolicyRequest | None = None


class ActivateSubscriptionRequest(BaseModel):
    expires_at: datetime | None = None


class RenewSubscriptionRequest(BaseModel):
    new_expires_at: datetime


class SubscriptionResponse(BaseModel):
    id: UUID
    subject: SubjectReferenceSchema
    plan_id: UUID
    subscription_type: SubscriptionType
    source: SubscriptionSource
    status: SubscriptionStatus
    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None
    trial_started_at: datetime | None
    cancelled_at: datetime | None
    expired_at: datetime | None
