from uuid import UUID

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from identity.application.contracts.repositories import OtpChallengeRepository
from identity.domain import OtpChallenge, OtpPurpose
from identity.infrastructure.persistence.sqlalchemy.mappers import OtpChallengeMapper
from identity.infrastructure.persistence.sqlalchemy.models import OtpChallengeModel


class SqlAlchemyOtpChallengeRepository(OtpChallengeRepository):
    def __init__(self, session: AsyncSession, mapper: OtpChallengeMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_latest(
        self,
        destination: str,
        purpose: OtpPurpose,
    ) -> OtpChallenge | None:
        statement = (
            select(OtpChallengeModel)
            .where(
                OtpChallengeModel.normalized_destination == destination,
                OtpChallengeModel.purpose == purpose,
            )
            .order_by(desc(OtpChallengeModel.created_at))
            .limit(1)
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def get(self, challenge_id: UUID) -> OtpChallenge | None:
        model = await self._session.get(OtpChallengeModel, challenge_id)
        return self._mapper.to_domain(model) if model is not None else None

    async def get_for_update(self, challenge_id: UUID) -> OtpChallenge | None:
        statement = (
            select(OtpChallengeModel).where(OtpChallengeModel.id == challenge_id).with_for_update()
        )
        model = await self._session.scalar(statement)
        return self._mapper.to_domain(model) if model is not None else None

    async def increment_attempts(self, challenge_id: UUID) -> None:
        statement = (
            update(OtpChallengeModel)
            .where(OtpChallengeModel.id == challenge_id)
            .values(attempts_count=OtpChallengeModel.attempts_count + 1)
        )
        await self._session.execute(statement)

    async def add(self, challenge: OtpChallenge) -> None:
        self._session.add(self._mapper.to_model(challenge))

    async def save(self, challenge: OtpChallenge) -> None:
        await self._session.merge(self._mapper.to_model(challenge))
