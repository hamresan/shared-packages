"""Host-owned SQLAlchemy models. No reusable-package tables are imported."""

from sqlalchemy import Column, MetaData, String, Table, UniqueConstraint

host_metadata = MetaData()

instagram_connection_links = Table(
    "host_instagram_connection_links",
    host_metadata,
    Column("connection_id", String(36), primary_key=True),
    Column("owner_user_id", String(36), nullable=False),
    Column("provider_account_id", String(128), nullable=False),
    UniqueConstraint("provider_account_id", name="uq_host_instagram_provider_account"),
)
