"""Privacy-minimized immutable security events in the Customer transaction."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from customer.application.actor import CustomerActorType


@dataclass(frozen=True, slots=True)
class CustomerAuditEvent:
    business_id: UUID
    customer_id: UUID
    actor_id: UUID
    actor_type: CustomerActorType
    action: str


class CustomerAuditRepository(Protocol):
    async def add(self, event: CustomerAuditEvent) -> None: ...
