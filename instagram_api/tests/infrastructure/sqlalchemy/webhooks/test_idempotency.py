"""Durable SQLAlchemy webhook idempotency tests."""

import asyncio
from datetime import timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from instagram_api.infrastructure.sqlalchemy.webhooks import (
    SqlAlchemyInstagramWebhookIdempotencyStore,
    SqlAlchemyInstagramWebhookSchema,
    instagram_webhook_events,
)


def build_engine(database_path: Path) -> AsyncEngine:
    """Build an isolated async SQLite engine for durability tests."""

    return create_async_engine(f"sqlite+aiosqlite:///{database_path}")


async def create_store(
    engine: AsyncEngine,
    *,
    lease_duration: timedelta = timedelta(minutes=5),
) -> SqlAlchemyInstagramWebhookIdempotencyStore:
    """Create the schema and return one durable store instance."""

    await SqlAlchemyInstagramWebhookSchema(engine).create()
    return SqlAlchemyInstagramWebhookIdempotencyStore(
        engine,
        lease_duration=lease_duration,
    )


def test_two_store_instances_atomically_suppress_duplicate_claim(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = build_engine(tmp_path / "atomic.db")
        try:
            first = await create_store(engine)
            second = SqlAlchemyInstagramWebhookIdempotencyStore(engine)

            assert await first.acquire("event-a") is True
            assert await second.acquire("event-a") is False
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_completed_event_remains_permanently_suppressed(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = build_engine(tmp_path / "completed.db")
        try:
            store = await create_store(engine)

            assert await store.acquire("event-a") is True
            await store.complete("event-a")
            assert await store.acquire("event-a") is False

            async with engine.connect() as connection:
                status = await connection.scalar(
                    select(instagram_webhook_events.c.status).where(
                        instagram_webhook_events.c.event_id == "event-a"
                    )
                )
            assert status == "completed"
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_released_retryable_event_can_be_claimed_again(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = build_engine(tmp_path / "release.db")
        try:
            first = await create_store(engine)
            second = SqlAlchemyInstagramWebhookIdempotencyStore(engine)

            assert await first.acquire("event-a") is True
            await first.release("event-a")
            assert await second.acquire("event-a") is True
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_expired_processing_lease_can_be_reclaimed_after_worker_loss(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        engine = build_engine(tmp_path / "lease.db")
        try:
            expired = await create_store(
                engine,
                lease_duration=timedelta(seconds=-1),
            )
            healthy = SqlAlchemyInstagramWebhookIdempotencyStore(engine)

            assert await expired.acquire("event-a") is True
            assert await healthy.acquire("event-a") is True
        finally:
            await engine.dispose()

    asyncio.run(scenario())
