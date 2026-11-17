from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CustomerCreationReceipt:
    business_id: UUID
    key: str
    fingerprint: str
    customer_id: UUID


class CustomerIdempotencyRepository(Protocol):
    async def lock_key(self, business_id: UUID, key: str) -> None: ...

    async def find(self, business_id: UUID, key: str) -> CustomerCreationReceipt | None: ...

    async def add(self, receipt: CustomerCreationReceipt) -> None: ...

    async def prune_expired(self, business_id: UUID, before: datetime) -> int: ...
