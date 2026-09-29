from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from identity.domain import IdentityType
from identity.infrastructure.persistence.sqlalchemy.mappers import UserIdentityMapper
from identity.infrastructure.persistence.sqlalchemy.repositories.user_identities import (
    SqlAlchemyUserIdentityRepository,
)
from identity.domain import UserIdentity
from identity.public import PublicIdentityUserResolver


async def test_resolves_registered_mobile_user(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    user_id = uuid4()
    now = datetime.now(UTC)
    async with session_factory() as session:
        repository = SqlAlchemyUserIdentityRepository(session, UserIdentityMapper())
        await repository.add(
            UserIdentity(
                id=uuid4(),
                user_id=user_id,
                type=IdentityType.MOBILE,
                value="+968 9123 4567",
                normalized_value="+96891234567",
                verified_at=now,
                created_at=now,
                updated_at=now,
            )
        )
        await session.commit()

    resolved = await PublicIdentityUserResolver(session_factory).resolve_user_id(
        IdentityType.MOBILE,
        "+968 9123 4567",
    )

    assert resolved == user_id


async def test_returns_none_for_unknown_or_invalid_mobile(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    resolver = PublicIdentityUserResolver(session_factory)

    assert await resolver.resolve_user_id(IdentityType.MOBILE, "+96890000000") is None
    assert await resolver.resolve_user_id(IdentityType.MOBILE, "invalid") is None
