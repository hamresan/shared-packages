from datetime import UTC, datetime
from uuid import UUID, uuid4

from store.domain import Store


def build_store(
    *,
    store_id: UUID | None = None,
    owner_user_id: UUID | None = None,
) -> Store:
    now = datetime(2026, 8, 17, 8, 0, tzinfo=UTC)
    return Store(
        id=store_id or uuid4(),
        owner_user_id=owner_user_id or uuid4(),
        name="Test Store",
        created_at=now,
        updated_at=now,
    )
