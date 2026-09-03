from datetime import UTC, datetime

from instagram_auth.application.models import InstagramAuthorizationGrant


def test_authorization_grant_keeps_transient_provider_data_outside_domain_entity() -> None:
    expires_at = datetime(2026, 9, 3, 13, 0, tzinfo=UTC)

    grant = InstagramAuthorizationGrant(
        access_token="transient-provider-token",
        expires_at=expires_at,
    )

    assert grant.access_token == "transient-provider-token"
    assert grant.expires_at == expires_at
