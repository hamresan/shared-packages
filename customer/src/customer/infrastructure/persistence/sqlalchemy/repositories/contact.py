from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.contact_repository import CustomerContactRepository
from customer.domain.contact import ContactKind, CustomerContact
from customer.infrastructure.persistence.sqlalchemy.mappers.contact import ContactMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerContactModel


class SqlAlchemyContactRepository(CustomerContactRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerContact, ...]:
        rows = (
            await self.session.scalars(
                select(CustomerContactModel)
                .where(
                    CustomerContactModel.business_id == business_id,
                    CustomerContactModel.customer_id == customer_id,
                )
                .order_by(CustomerContactModel.created_at, CustomerContactModel.id)
            )
        ).all()
        return tuple(ContactMapper.to_domain(row) for row in rows)

    async def get(
        self, business_id: UUID, customer_id: UUID, contact_id: UUID
    ) -> CustomerContact | None:
        row = await self.session.scalar(
            select(CustomerContactModel).where(
                CustomerContactModel.business_id == business_id,
                CustomerContactModel.customer_id == customer_id,
                CustomerContactModel.id == contact_id,
            )
        )
        return ContactMapper.to_domain(row) if row is not None else None

    async def add(self, contact: CustomerContact) -> None:
        self.session.add(ContactMapper.to_row(contact))

    async def save(self, contact: CustomerContact) -> None:
        await self.session.execute(
            update(CustomerContactModel)
            .where(
                CustomerContactModel.id == contact.id,
                CustomerContactModel.business_id == contact.business_id,
                CustomerContactModel.customer_id == contact.customer_id,
            )
            .values(
                value=contact.value,
                kind=contact.kind.value,
                is_primary=contact.is_primary,
                verified_at=contact.verified_at,
                verification_method=contact.verification_method,
            )
        )

    async def remove(self, business_id: UUID, customer_id: UUID, contact_id: UUID) -> None:
        await self.session.execute(
            delete(CustomerContactModel).where(
                CustomerContactModel.business_id == business_id,
                CustomerContactModel.customer_id == customer_id,
                CustomerContactModel.id == contact_id,
            )
        )

    async def unset_primary(self, business_id: UUID, customer_id: UUID, kind: ContactKind) -> None:
        await self.session.execute(
            update(CustomerContactModel)
            .where(
                CustomerContactModel.business_id == business_id,
                CustomerContactModel.customer_id == customer_id,
                CustomerContactModel.kind == kind.value,
            )
            .values(is_primary=False)
        )
