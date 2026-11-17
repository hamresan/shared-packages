from uuid import UUID

from customer.application.contracts import CustomerCreationReceipt, CustomerIdempotencyRepository


class InMemoryCustomerIdempotencyRepository(CustomerIdempotencyRepository):
    async def lock_key(self, business_id: UUID, key: str) -> None:
        return None

    def __init__(self) -> None:
        self.records: dict[tuple[UUID, str], CustomerCreationReceipt] = {}

    async def find(self, business_id: UUID, key: str) -> CustomerCreationReceipt | None:
        return self.records.get((business_id, key))

    async def add(self, receipt: CustomerCreationReceipt) -> None:
        self.records[(receipt.business_id, receipt.key)] = receipt
