"""SQLAlchemy table definition for durable webhook idempotency."""

from sqlalchemy import Column, DateTime, MetaData, String, Table, func

metadata = MetaData()

instagram_webhook_events = Table(
    "instagram_webhook_events",
    metadata,
    Column("event_id", String(64), primary_key=True),
    Column("status", String(16), nullable=False),
    Column(
        "lease_expires_at",
        DateTime(timezone=True),
        nullable=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "completed_at",
        DateTime(timezone=True),
        nullable=True,
    ),
)
