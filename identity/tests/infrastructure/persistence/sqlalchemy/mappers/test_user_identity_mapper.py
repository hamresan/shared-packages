from datetime import UTC, datetime
from uuid import uuid4

from identity.domain import IdentityType, UserIdentity
from identity.infrastructure.persistence.sqlalchemy.mappers import UserIdentityMapper


def test_user_identity_mapper_round_trip() -> None:
    now = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)
    identity = UserIdentity(
        id=uuid4(),
        user_id=uuid4(),
        type=IdentityType.EMAIL,
        value="user@example.com",
        normalized_value="user@example.com",
        verified_at=now,
        created_at=now,
        updated_at=now,
    )

    mapper = UserIdentityMapper()
    mapped = mapper.to_domain(mapper.to_model(identity))

    assert mapped == identity
