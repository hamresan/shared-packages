from datetime import UTC, datetime
from uuid import UUID

from identity.application.contracts.database import AsyncSessionFactory
from identity.domain import User
from identity.infrastructure.persistence.sqlalchemy.mappers import UserMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserModel
from sqlalchemy import select


class PublicIdentityUserProfileWriter:
    """Update profile fields owned by the Identity module."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory
        self._mapper = UserMapper()

    async def update_full_name(self, user_id: UUID, full_name: str) -> User:
        normalized_name = full_name.strip()
        if not normalized_name:
            raise ValueError("Full name is required.")
        async with self._session_factory() as session:
            model = await session.scalar(select(UserModel).where(UserModel.id == user_id))
            if model is None:
                raise ValueError("Identity user was not found.")
            model.full_name = normalized_name
            model.updated_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(model)
        return self._mapper.to_domain(model)
