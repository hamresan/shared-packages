"""Application error contracts."""

from instagram_auth.application.errors.access import (
    InstagramConnectionAccessError,
    InstagramConnectionPermissionError,
    InstagramConnectionUnavailableError,
)
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionIdentityMismatchError,
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
    "InstagramConnectionAccessError",
    "InstagramConnectionConcurrencyError",
    "InstagramConnectionIdentityMismatchError",
    "InstagramConnectionNotFoundError",
    "InstagramConnectionOwnershipError",
    "InstagramConnectionPermissionError",
    "InstagramConnectionUnavailableError",
    "InstagramProviderError",
]
