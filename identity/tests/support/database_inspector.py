from uuid import UUID

from sqlalchemy import func, select

from identity.infrastructure.persistence.sqlalchemy.models import OtpChallengeModel, SessionModel
from tests.support.database_contracts import IdentityTestDatabase


class IdentityDatabaseInspector:
    def __init__(self, database: IdentityTestDatabase) -> None:
        self._database = database

    async def count_sessions(self) -> int:
        async with self._database.session_factory() as session:
            value = await session.scalar(select(func.count(SessionModel.id)))
            return int(value or 0)

    async def get_otp_attempts_count(self, challenge_id: UUID) -> int:
        async with self._database.session_factory() as session:
            value = await session.scalar(
                select(OtpChallengeModel.attempts_count).where(OtpChallengeModel.id == challenge_id)
            )
            if value is None:
                raise AssertionError(f"OTP challenge {challenge_id} was not found")
            return value
