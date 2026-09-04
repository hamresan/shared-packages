"""Host Alembic integration point for the reference consumer."""

from sqlalchemy import MetaData

from .models import host_metadata


def get_host_alembic_target_metadata() -> MetaData:
    """Return only host-owned metadata for the host's Alembic environment."""

    return host_metadata
