from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CustomerCreationReceipt:
    business_id: UUID
    key: str
    fingerprint: str
    customer_id: UUID


class CustomerIdempotencyRepository(Protocol):
    async def find(self, business_id: UUID, key: str) -> CustomerCreationReceipt | None: ...

    async def add(self, receipt: CustomerCreationReceipt) -> None: ...
