from datetime import datetime

from pydantic import BaseModel, Field

from subscription.domain import UsagePeriod
from subscription.presentation.schemas.common import SubjectReferenceSchema


class RecordUsageRequest(BaseModel):
    subject: SubjectReferenceSchema
    metric: str = Field(min_length=1, max_length=128)
    amount: int = Field(default=1, gt=0)


class UsageRecordResponse(BaseModel):
    subject: SubjectReferenceSchema
    metric: str
    amount: int
    occurred_at: datetime


class UsageCounterResponse(BaseModel):
    metric: str
    period: UsagePeriod
    consumed: int
