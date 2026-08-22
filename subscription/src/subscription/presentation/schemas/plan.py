from uuid import UUID

from pydantic import BaseModel, Field

from subscription.domain import PlanStatus, SubscriptionType
from subscription.presentation.schemas.common import EntitlementValueSchema


class PlanEntitlementRequest(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    value: EntitlementValueSchema


class CreatePlanRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    subscription_type: SubscriptionType
    status: PlanStatus = PlanStatus.ACTIVE
    entitlements: list[PlanEntitlementRequest] = Field(default_factory=list)


class ChangePlanStatusRequest(BaseModel):
    status: PlanStatus


class PlanEntitlementResponse(BaseModel):
    key: str
    value: EntitlementValueSchema


class PlanResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    subscription_type: SubscriptionType
    status: PlanStatus
    entitlements: list[PlanEntitlementResponse]
