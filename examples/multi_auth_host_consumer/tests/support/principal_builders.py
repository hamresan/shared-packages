"""Principal builders for the multi-auth host example tests."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from identity.public import AuthenticatedPrincipal
from integration_auth import IntegrationClientId, IntegrationPrincipal, IntegrationScope, Permission


class IdentityPrincipalBuilder:
    """Build a deterministic human principal."""

    def build(self) -> AuthenticatedPrincipal:
        issued_at = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
        return AuthenticatedPrincipal(
            user_id=UUID("11111111-1111-1111-1111-111111111111"),
            session_id=UUID("22222222-2222-2222-2222-222222222222"),
            authentication_method="otp",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(hours=1),
        )


class IntegrationPrincipalBuilder:
    """Build a deterministic machine principal."""

    def build(self) -> IntegrationPrincipal:
        return IntegrationPrincipal(
            client_id=IntegrationClientId("client-123"),
            permissions=frozenset({Permission("orders.read"), Permission("catalog.read")}),
            scopes=frozenset({IntegrationScope("store", "store-123")}),
        )
