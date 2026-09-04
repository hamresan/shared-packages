"""Verify host composition with the hamresan-identity public contract."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from identity.public import AuthenticatedPrincipal

from instagram_auth.application.linking import (
    InstagramHostIdentityHandoff,
    InstagramHostLinkAction,
)
from instagram_auth.baseline import InstagramAccountType
from instagram_auth.domain import InstagramExternalIdentity
from tests.integration.support import IdentityPrincipalOwnerAdapter

NOW = datetime(2026, 9, 4, tzinfo=UTC)


def test_authenticated_identity_principal_can_scope_additional_instagram_connection() -> None:
    principal = AuthenticatedPrincipal(
        user_id=UUID("00000000-0000-0000-0000-000000000501"),
        session_id=UUID("00000000-0000-0000-0000-000000000502"),
        authentication_method="otp",
        issued_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )
    owner_user_id = IdentityPrincipalOwnerAdapter().owner_user_id(principal)

    handoff = InstagramHostIdentityHandoff(
        identity=InstagramExternalIdentity(
            provider_user_id="instagram-user-501",
            username="shop",
            account_type=InstagramAccountType.BUSINESS,
        ),
        action=InstagramHostLinkAction.ATTACH_TO_EXISTING_OWNER,
        owner_user_id=owner_user_id,
    )

    assert handoff.owner_user_id == str(principal.user_id)
    assert handoff.action is InstagramHostLinkAction.ATTACH_TO_EXISTING_OWNER
