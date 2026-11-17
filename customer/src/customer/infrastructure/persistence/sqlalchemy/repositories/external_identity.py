from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from customer.application.contracts.external_identity_repository import (
    CustomerExternalIdentityRepository,
)
from customer.domain.external_identity import CustomerExternalIdentity, ExternalIdentityKey
from customer.infrastructure.persistence.sqlalchemy.mappers.external_identity import (
    ExternalIdentityMapper,
)
from customer.infrastructure.persistence.sqlalchemy.models import CustomerExternalIdentityModel


class SqlAlchemyExternalIdentityRepository(CustomerExternalIdentityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def matching_key(self, key: ExternalIdentityKey) -> tuple[ColumnElement[bool], ...]:
        return (
            CustomerExternalIdentityModel.business_id == key.business_id,
            CustomerExternalIdentityModel.provider == key.provider,
            CustomerExternalIdentityModel.channel_account_id == key.channel_account_id,
            CustomerExternalIdentityModel.external_user_id == key.external_user_id,
        )

    async def find_active(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None:
        row = await self.session.scalar(
            select(CustomerExternalIdentityModel).where(
                *self.matching_key(key), CustomerExternalIdentityModel.status == "active"
            )
        )
        return ExternalIdentityMapper.to_domain(row) if row is not None else None

    async def find_latest(self, key: ExternalIdentityKey) -> CustomerExternalIdentity | None:
        row = await self.session.scalar(
            select(CustomerExternalIdentityModel)
            .where(*self.matching_key(key))
            .order_by(
                CustomerExternalIdentityModel.linked_at.desc(),
                CustomerExternalIdentityModel.id.desc(),
            )
            .limit(1)
        )
        return ExternalIdentityMapper.to_domain(row) if row is not None else None

    async def get_active_for_customer(
        self, key: ExternalIdentityKey, customer_id: UUID
    ) -> CustomerExternalIdentity | None:
        row = await self.session.scalar(
            select(CustomerExternalIdentityModel).where(
                *self.matching_key(key),
                CustomerExternalIdentityModel.customer_id == customer_id,
                CustomerExternalIdentityModel.status == "active",
            )
        )
        return ExternalIdentityMapper.to_domain(row) if row is not None else None

    async def add(self, identity: CustomerExternalIdentity) -> None:
        self.session.add(ExternalIdentityMapper.to_row(identity))

    async def save(self, identity: CustomerExternalIdentity) -> None:
        await self.session.execute(
            update(CustomerExternalIdentityModel)
            .where(
                CustomerExternalIdentityModel.id == identity.id, *self.matching_key(identity.key)
            )
            .values(
                status=identity.status.value,
                revoked_at=identity.revoked_at,
                verification_method=identity.verification_method,
                verified_at=identity.verified_at,
            )
        )
