from customer.application.contracts.audit_repository import (
    CustomerAuditEvent,
    CustomerAuditRepository,
)


class InMemoryAuditRepository(CustomerAuditRepository):
    def __init__(self) -> None:
        self.events: list[CustomerAuditEvent] = []

    async def add(self, event: CustomerAuditEvent) -> None:
        self.events.append(event)
