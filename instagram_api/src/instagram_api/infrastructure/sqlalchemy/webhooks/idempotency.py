"""Durable SQLAlchemy webhook idempotency store."""

from sqlalchemy import delete, insert, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from instagram_api.application.contracts.webhooks import InstagramWebhookIdempotencyStore

from .models import instagram_webhook_events

_STATUS_PROCESSING = "processing"
_STATUS_COMPLETED = "completed"


class SqlAlchemyInstagramWebhookIdempotencyStore(InstagramWebhookIdempotencyStore):
    """Uses a database primary key as the atomic cross-worker claim."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def acquire(self, event_id: str) -> bool:
        """Atomically claim an unseen event."""

        try:
            async with self._engine.begin() as connection:
                await connection.execute(
                    insert(instagram_webhook_events).values(
                        event_id=event_id,
                        status=_STATUS_PROCESSING,
                    )
                )
        except IntegrityError:
            return False
        return True

    async def complete(self, event_id: str) -> None:
        """Mark a claimed event as completed."""

        async with self._engine.begin() as connection:
            await connection.execute(
                update(instagram_webhook_events)
                .where(instagram_webhook_events.c.event_id == event_id)
                .values(
                    status=_STATUS_COMPLETED,
                    completed_at=__import__("datetime").datetime.now(
                        __import__("datetime").UTC
                    ),
                )
            )

    async def release(self, event_id: str) -> None:
        """Release only an in-progress claim after a retryable failure."""

        async with self._engine.begin() as connection:
            await connection.execute(
                delete(instagram_webhook_events).where(
                    instagram_webhook_events.c.event_id == event_id,
                    instagram_webhook_events.c.status == _STATUS_PROCESSING,
                )
            )
