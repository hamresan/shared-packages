from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.audit_repository import (
    CustomerAuditEvent,
    CustomerAuditRepository,
)
from customer.infrastructure.persistence.sqlalchemy.models import CustomerAuditModel


class SqlAlchemyAuditRepository(CustomerAuditRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, event: CustomerAuditEvent) -> None:
        self.session.add(
            CustomerAuditModel(
                id=uuid4(),
                business_id=event.business_id,
                customer_id=event.customer_id,
                actor_id=event.actor_id,
                actor_type=event.actor_type.value,
                action=event.action,
            )
        )
