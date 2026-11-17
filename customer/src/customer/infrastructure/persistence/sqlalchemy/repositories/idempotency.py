from datetime import datetime
from uuid import UUID

from sqlalchemy import CursorResult, delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.idempotency_repository import (
    CustomerCreationReceipt,
    CustomerIdempotencyRepository,
)
from customer.infrastructure.persistence.sqlalchemy.mappers.idempotency import IdempotencyMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerCreationReceiptModel


class SqlAlchemyIdempotencyRepository(CustomerIdempotencyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def lock_key(self, business_id: UUID, key: str) -> None:
        if self.session.bind is not None and self.session.bind.dialect.name == "postgresql":
            await self.session.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:namespace, 0))"),
                {"namespace": f"customer:create:{business_id}:{key}"},
            )

    async def find(self, business_id: UUID, key: str) -> CustomerCreationReceipt | None:
        row = await self.session.scalar(
            select(CustomerCreationReceiptModel).where(
                CustomerCreationReceiptModel.business_id == business_id,
                CustomerCreationReceiptModel.key == key,
            )
        )
        return IdempotencyMapper.to_domain(row) if row is not None else None

    async def add(self, receipt: CustomerCreationReceipt) -> None:
        self.session.add(IdempotencyMapper.to_row(receipt))

    async def prune_expired(self, business_id: UUID, before: datetime) -> int:
        result = await self.session.execute(
            delete(CustomerCreationReceiptModel).where(
                CustomerCreationReceiptModel.business_id == business_id,
                CustomerCreationReceiptModel.created_at < before,
            )
        )
        return result.rowcount if isinstance(result, CursorResult) else 0
