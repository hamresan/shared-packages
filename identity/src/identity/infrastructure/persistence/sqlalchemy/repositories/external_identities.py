from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.repositories import ExternalIdentityRepository
from identity.domain import ExternalIdentity
from identity.infrastructure.persistence.sqlalchemy.mappers.external_identity import (
    ExternalIdentityMapper,
)
from identity.infrastructure.persistence.sqlalchemy.models import ExternalIdentityModel


class SqlAlchemyExternalIdentityRepository(ExternalIdentityRepository):
    def __init__(self, session: AsyncSession, mapper: ExternalIdentityMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_by_provider_subject(
        self,
        provider: str,
        subject: str,
    ) -> ExternalIdentity | None:
        statement = select(ExternalIdentityModel).where(
            ExternalIdentityModel.provider == provider,
            ExternalIdentityModel.subject == subject,
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def add(self, external_identity: ExternalIdentity) -> None:
        self._session.add(self._mapper.to_model(external_identity))
        await self._session.flush()
