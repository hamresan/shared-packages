from datetime import UTC, datetime, timedelta
from uuid import uuid4

from identity.domain import Session
from identity.infrastructure.persistence.sqlalchemy.mappers import SessionMapper


def test_session_mapper_round_trip() -> None:
    now = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)
    session = Session(
        id=uuid4(),
        user_id=uuid4(),
        refresh_token_hash="refresh-hash",
        family_id=uuid4(),
        parent_session_id=None,
        replaced_by_session_id=None,
        expires_at=now + timedelta(days=30),
        family_expires_at=now + timedelta(days=90),
        revoked_at=None,
        device_info="browser",
        ip_address="203.0.113.10",
        created_at=now,
        last_used_at=None,
    )

    mapper = SessionMapper()
    mapped = mapper.to_domain(mapper.to_model(session))

    assert mapped == session
