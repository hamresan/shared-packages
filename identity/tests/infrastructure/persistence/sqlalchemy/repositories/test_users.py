from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from identity.domain import User, UserStatus
from identity.infrastructure.persistence.sqlalchemy.mappers import UserMapper
from identity.infrastructure.persistence.sqlalchemy.repositories.users import SqlAlchemyUserRepository


async def test_add_flushes_user_before_dependent_writes() -> None:
    session = MagicMock(spec=AsyncSession)
    session.flush = AsyncMock()
    repository = SqlAlchemyUserRepository(session, UserMapper())
    now = datetime.now(UTC)
    user = User(
        id=uuid4(),
        full_name="Repository Test",
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    await repository.add(user)

    session.add.assert_called_once()
    session.flush.assert_awaited_once_with()
