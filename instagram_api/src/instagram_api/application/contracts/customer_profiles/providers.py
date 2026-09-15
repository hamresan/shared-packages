"""Provider boundary for Instagram customer profile data."""

from typing import Protocol

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramCustomerProfile,
    InstagramUserId,
)


class InstagramCustomerProfileProvider(Protocol):
    """Reads one Instagram messaging customer's provider-owned profile."""

    async def get_customer_profile(
        self,
        connection_id: InstagramConnectionId,
        user_id: InstagramUserId,
    ) -> InstagramCustomerProfile:
        """Return normalized profile data for the selected Instagram-scoped user."""
        ...
