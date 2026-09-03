"""Application error contracts."""

from instagram_auth.application.errors.connection_access import (
    InstagramConnectionNotFoundError,
    InstagramConnectionOwnershipError,
)
from instagram_auth.application.errors.persistence import (
    DuplicateInstagramConnectionError,
    InstagramConnectionConcurrencyError,
)
from instagram_auth.application.errors.provider_error import InstagramProviderError

__all__ = [
    "DuplicateInstagramConnectionError",
    "InstagramConnectionConcurrencyError",
    "InstagramConnectionNotFoundError",
    "InstagramConnectionOwnershipError",
    "InstagramProviderError",
]
