from uuid import UUID

from pydantic import BaseModel

from subscription.presentation.schemas.common import EntitlementValueSchema


class EntitlementGrantResponse(BaseModel):
    subscription_id: UUID
    plan_id: UUID
    value: EntitlementValueSchema


class EntitlementResponse(BaseModel):
    grants: list[EntitlementGrantResponse]
