from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.internal_identity_repository import (
    CustomerIdentityLinkRepository,
)
from customer.domain.identity_link import CustomerIdentityLink
from customer.infrastructure.persistence.sqlalchemy.mappers.internal_identity import (
    InternalIdentityMapper,
)
from customer.infrastructure.persistence.sqlalchemy.models import CustomerIdentityLinkModel


class SqlAlchemyInternalIdentityRepository(CustomerIdentityLinkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> CustomerIdentityLink | None:
        row = await self.session.scalar(
            select(CustomerIdentityLinkModel).where(
                CustomerIdentityLinkModel.business_id == business_id,
                CustomerIdentityLinkModel.customer_id == customer_id,
                CustomerIdentityLinkModel.revoked_at.is_(None),
            )
        )
        return InternalIdentityMapper.to_domain(row) if row is not None else None

    async def find_by_user(
        self, business_id: UUID, identity_user_id: UUID
    ) -> CustomerIdentityLink | None:
        row = await self.session.scalar(
            select(CustomerIdentityLinkModel).where(
                CustomerIdentityLinkModel.business_id == business_id,
                CustomerIdentityLinkModel.identity_user_id == identity_user_id,
                CustomerIdentityLinkModel.revoked_at.is_(None),
            )
        )
        return InternalIdentityMapper.to_domain(row) if row is not None else None

    async def add(self, link: CustomerIdentityLink) -> None:
        self.session.add(InternalIdentityMapper.to_row(link))

    async def revoke(self, link: CustomerIdentityLink) -> None:
        await self.session.execute(
            update(CustomerIdentityLinkModel)
            .where(
                CustomerIdentityLinkModel.business_id == link.business_id,
                CustomerIdentityLinkModel.customer_id == link.customer_id,
                CustomerIdentityLinkModel.id == link.id,
            )
            .values(revoked_at=link.revoked_at)
        )
