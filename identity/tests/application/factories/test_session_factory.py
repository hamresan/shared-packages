from datetime import UTC, datetime, timedelta
from uuid import uuid4

from identity.application.factories.entities import SessionFactory


def test_session_factory_preserves_absolute_family_expiration_across_rotation() -> None:
    started_at = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)
    factory = SessionFactory(
        ttl=timedelta(days=30),
        absolute_ttl=timedelta(days=90),
    )

    initial = factory.create(
        now=started_at,
        user_id=uuid4(),
        refresh_token_hash="initial-refresh-hash",
        device_info=None,
        ip_address=None,
    )
    replacement = factory.create(
        now=started_at + timedelta(days=80),
        user_id=initial.user_id,
        refresh_token_hash="replacement-refresh-hash",
        device_info=None,
        ip_address=None,
        family_id=initial.family_id,
        parent_session_id=initial.id,
        family_expires_at=initial.family_expires_at,
    )

    assert initial.expires_at == started_at + timedelta(days=30)
    assert initial.family_expires_at == started_at + timedelta(days=90)
    assert replacement.family_expires_at == initial.family_expires_at
    assert replacement.expires_at == initial.family_expires_at
