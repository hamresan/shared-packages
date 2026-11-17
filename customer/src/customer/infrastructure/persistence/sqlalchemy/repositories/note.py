from uuid import UUID

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.note_repository import CustomerNoteRepository
from customer.domain.note import CustomerNote
from customer.infrastructure.persistence.sqlalchemy.mappers.note import NoteMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerNoteModel


class SqlAlchemyNoteRepository(CustomerNoteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerNote, ...]:
        rows = (
            await self.session.scalars(
                select(CustomerNoteModel)
                .where(
                    CustomerNoteModel.business_id == business_id,
                    CustomerNoteModel.customer_id == customer_id,
                )
                .order_by(CustomerNoteModel.created_at, CustomerNoteModel.id)
            )
        ).all()
        return tuple(NoteMapper.to_domain(row) for row in rows)

    async def add(self, note: CustomerNote) -> None:
        self.session.add(NoteMapper.to_row(note))

    async def remove(self, business_id: UUID, customer_id: UUID, note_id: UUID) -> bool:
        result = await self.session.execute(
            delete(CustomerNoteModel).where(
                CustomerNoteModel.business_id == business_id,
                CustomerNoteModel.customer_id == customer_id,
                CustomerNoteModel.id == note_id,
            )
        )
        return isinstance(result, CursorResult) and result.rowcount == 1
