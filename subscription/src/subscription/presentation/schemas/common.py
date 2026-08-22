from decimal import Decimal

from pydantic import BaseModel, Field

from subscription.domain import EntitlementValueType, UsagePeriod


class SubjectReferenceSchema(BaseModel):
    subject_type: str = Field(min_length=1, max_length=64)
    subject_id: str = Field(min_length=1, max_length=255)


class EntitlementValueSchema(BaseModel):
    value_type: EntitlementValueType
    value: bool | int | Decimal | str | None = None


class UsageConditionSchema(BaseModel):
    metric: str = Field(min_length=1, max_length=128)
    limit: int = Field(gt=0)
    period: UsagePeriod = UsagePeriod.TRIAL
