"""Tests for atomic SQLAlchemy nonce consumption."""

import asyncio
from pathlib import Path

from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.infrastructure.persistence.sqlalchemy.repositories.nonce_store import (
    SqlAlchemyNonceStore,
)
from tests.support.infrastructure.persistence.sqlalchemy.database import SqlAlchemyTestDatabase


def test_nonce_store_allows_only_one_concurrent_consumer(tmp_path: Path) -> None:
    async def run() -> None:
        database = SqlAlchemyTestDatabase(tmp_path / "nonces.db")
        await database.create_schema()
        store = SqlAlchemyNonceStore(database.session_factory)
        client_id = IntegrationClientId("client-123")

        results = await asyncio.gather(
            *(
                store.consume_once(
                    client_id=client_id,
                    nonce="same-nonce",
                    expires_at_timestamp=2_000_000_000,
                )
                for _ in range(8)
            )
        )

        assert results.count(True) == 1
        assert results.count(False) == 7
        assert await store.consume_once(
            client_id=IntegrationClientId("client-other"),
            nonce="same-nonce",
            expires_at_timestamp=2_000_000_000,
        )
        await database.dispose()

    asyncio.run(run())
