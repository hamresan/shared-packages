from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.models.profile_detail_commands import CustomerDetailsQuery


@dataclass(frozen=True, slots=True)
class LinkInternalIdentityCommand(CustomerDetailsQuery):
    identity_user_id: UUID


@dataclass(frozen=True, slots=True)
class ResolveInternalIdentityQuery:
    business_id: UUID
    actor: CustomerActor
    identity_user_id: UUID
