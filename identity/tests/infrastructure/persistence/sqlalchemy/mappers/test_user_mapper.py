from datetime import UTC, datetime
from uuid import uuid4

from identity.domain import User, UserStatus
from identity.infrastructure.persistence.sqlalchemy.mappers import UserMapper


def test_user_mapper_round_trip() -> None:
    now = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)
    user = User(
        id=uuid4(),
        full_name="Mapper Test User",
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    mapper = UserMapper()
    mapped = mapper.to_domain(mapper.to_model(user))

    assert mapped == user
