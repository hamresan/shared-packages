"""Connection models owned by the Instagram API boundary."""

from dataclasses import dataclass

from .identifiers import InstagramAccountId, InstagramConnectionId


@dataclass(frozen=True, slots=True)
class InstagramConnection:
    """Connection context required by account-scoped operations."""

    id: InstagramConnectionId
    provider_account_id: InstagramAccountId
    permissions: frozenset[str]
    is_usable: bool
