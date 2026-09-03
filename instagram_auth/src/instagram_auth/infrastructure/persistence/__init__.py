"""SQLAlchemy persistence adapters for Instagram authentication."""

from instagram_auth.infrastructure.persistence.alembic import (
    get_instagram_auth_metadata,
    is_instagram_auth_table,
)
from instagram_auth.infrastructure.persistence.base import InstagramAuthBase
from instagram_auth.infrastructure.persistence.models import InstagramConnectionRecord
from instagram_auth.infrastructure.persistence.repositories import (
    SqlAlchemyInstagramConnectionRepository,
    SqlAlchemyInstagramCredentialRepository,
)
from instagram_auth.infrastructure.persistence.unit_of_work import (
    SqlAlchemyInstagramAuthUnitOfWork,
)

__all__ = [
    "InstagramAuthBase",
    "InstagramConnectionRecord",
    "SqlAlchemyInstagramAuthUnitOfWork",
    "SqlAlchemyInstagramConnectionRepository",
    "SqlAlchemyInstagramCredentialRepository",
    "get_instagram_auth_metadata",
    "is_instagram_auth_table",
]
