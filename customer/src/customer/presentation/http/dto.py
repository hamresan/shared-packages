"""Transport-only request and response shapes."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = None


class CustomerUpdateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = None
    expected_version: int = Field(ge=1)


class CustomerResponse(BaseModel):
    id: UUID
    business_id: UUID
    display_name: str | None
    status: str
    version: int
    created_at: datetime
    updated_at: datetime


class ExternalIdentityResponse(BaseModel):
    customer_id: UUID
    business_id: UUID
    display_name: str | None
    identity_status: str
    verification_method: str
    verified_at: datetime


class ExternalIdentityLookupBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    channel_account_id: str = Field(min_length=1)
    external_user_id: str = Field(min_length=1)
