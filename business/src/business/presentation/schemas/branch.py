from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from business.domain.enums import BranchStatus


class BranchAddressSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    country_code: str | None = None
    state_or_province: str | None = None
    city: str | None = None
    area: str | None = None
    street: str | None = None
    building: str | None = None
    postal_code: str | None = None
    additional_details: str | None = None


class BranchContactSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    phone: str | None = None
    email: str | None = None


class CreateBranchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    timezone: str
    address: BranchAddressSchema | None = None
    contact: BranchContactSchema | None = None


class UpdateBranchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    timezone: str
    address: BranchAddressSchema | None = None
    contact: BranchContactSchema | None = None


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    business_id: UUID
    name: str
    timezone: str
    address: BranchAddressSchema | None
    contact: BranchContactSchema | None
    status: BranchStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
