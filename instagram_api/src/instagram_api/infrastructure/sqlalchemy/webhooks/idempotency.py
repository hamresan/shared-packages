"""Durable SQLAlchemy webhook idempotency store."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, insert, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from instagram_api.application.contracts.webhooks import InstagramWebhookIdempotencyStore

from .models import instagram_webhook_events

_STATUS_PROCESSING = "processing"
_STATUS_COMPLETED = "completed"
_DEFAULT_LEASE_DURATION = timedelta(minutes=5)


class SqlAlchemyInstagramWebhookIdempotencyStore(InstagramWebhookIdempotencyStore):
    """Uses database constraints and leases for atomic cross-worker claims."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        lease_duration: timedelta = _DEFAULT_LEASE_DURATION,
    ) -> None:
        self._engine = engine
        self._lease_duration = lease_duration

    async def acquire(self, event_id: str) -> bool:
        """Atomically claim an unseen event or reclaim an expired processing lease."""

        now = datetime.now(UTC)
        lease_expires_at = now + self._lease_duration

        try:
            async with self._engine.begin() as connection:
                await connection.execute(
                    insert(instagram_webhook_events).values(
                        event_id=event_id,
                        status=_STATUS_PROCESSING,
                        lease_expires_at=lease_expires_at,
                    )
                )
            return True
        except IntegrityError:
            async with self._engine.begin() as connection:
                result = await connection.execute(
                    update(instagram_webhook_events)
                    .where(
                        instagram_webhook_events.c.event_id == event_id,
                        instagram_webhook_events.c.status == _STATUS_PROCESSING,
                        instagram_webhook_events.c.lease_expires_at <= now,
                    )
                    .values(lease_expires_at=lease_expires_at)
                )
            return result.rowcount == 1

    async def complete(self, event_id: str) -> None:
        """Mark a claimed event as completed and permanently suppress duplicates."""

        async with self._engine.begin() as connection:
            await connection.execute(
                update(instagram_webhook_events)
                .where(
                    instagram_webhook_events.c.event_id == event_id,
                    instagram_webhook_events.c.status == _STATUS_PROCESSING,
                )
                .values(
                    status=_STATUS_COMPLETED,
                    lease_expires_at=None,
                    completed_at=datetime.now(UTC),
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
