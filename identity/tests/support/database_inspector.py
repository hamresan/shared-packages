from datetime import datetime
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

    async def count_active_sessions_in_family(self, family_id: UUID) -> int:
        async with self._database.session_factory() as session:
            value = await session.scalar(
                select(func.count(SessionModel.id)).where(
                    SessionModel.family_id == family_id,
                    SessionModel.revoked_at.is_(None),
                )
            )
            return int(value or 0)

    async def get_session_family_id(self, session_id: UUID) -> UUID:
        async with self._database.session_factory() as session:
            value = await session.scalar(
                select(SessionModel.family_id).where(SessionModel.id == session_id)
            )
            if value is None:
                raise AssertionError(f"Session {session_id} was not found")
            return value

    async def get_session_family_expires_at(self, session_id: UUID) -> datetime:
        async with self._database.session_factory() as session:
            value = await session.scalar(
                select(SessionModel.family_expires_at).where(SessionModel.id == session_id)
            )
            if value is None:
                raise AssertionError(f"Session {session_id} was not found")
            return value

    async def get_otp_attempts_count(self, challenge_id: UUID) -> int:
        async with self._database.session_factory() as session:
            value = await session.scalar(
                select(OtpChallengeModel.attempts_count).where(OtpChallengeModel.id == challenge_id)
            )
            if value is None:
                raise AssertionError(f"OTP challenge {challenge_id} was not found")
            return value
