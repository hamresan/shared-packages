"""Connection identifier generation boundary."""

from typing import Protocol

from instagram_auth.domain import InstagramConnectionId


class InstagramConnectionIdGenerator(Protocol):
    """Generate package-owned identifiers for new Instagram connections."""

    def generate(self) -> InstagramConnectionId:
        """Return a new connection identifier."""
        ...
