from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from business.domain.enums import BusinessStatus


class CreateBusinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    country_code: str
    default_language: str
    default_currency_code: str
    business_type: str | None = None


class UpdateBusinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    business_type: str | None = None


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    business_type: str | None
    country_code: str
    default_language: str
    default_currency_code: str
    status: BusinessStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
