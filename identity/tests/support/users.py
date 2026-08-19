from uuid import UUID

from sqlalchemy import update

from identity.application.contracts.database import AsyncSessionFactory
from identity.domain import UserStatus
from identity.infrastructure.persistence.sqlalchemy.models import UserModel


class SqlAlchemyUserStatusUpdater:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def set_status(self, user_id: UUID, status: UserStatus) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel).where(UserModel.id == user_id).values(status=status)
            )
            await session.commit()
