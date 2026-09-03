from urllib.parse import parse_qs, urlparse

import pytest

from instagram_auth.baseline import InstagramPermission
from instagram_auth.infrastructure.meta import MetaInstagramAuthorizationUrlBuilder


def test_meta_authorization_url_contains_encoded_oauth_parameters() -> None:
    builder = MetaInstagramAuthorizationUrlBuilder(client_id="app-123")

    url = builder.build(
        redirect_uri="https://app.example/oauth/callback?source=instagram",
        state="secure-state",
        permissions={
            InstagramPermission.BASIC,
            InstagramPermission.MANAGE_MESSAGES,
        },
    )

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == (
        "https://www.instagram.com/oauth/authorize"
    )
    assert query["client_id"] == ["app-123"]
    assert query["redirect_uri"] == ["https://app.example/oauth/callback?source=instagram"]
    assert query["response_type"] == ["code"]
    assert query["state"] == ["secure-state"]
    assert set(query["scope"][0].split(",")) == {
        "instagram_business_basic",
        "instagram_business_manage_messages",
    }


def test_meta_authorization_url_builder_rejects_missing_client_id() -> None:
    with pytest.raises(ValueError, match="client_id is required"):
        MetaInstagramAuthorizationUrlBuilder(client_id="")


def test_meta_authorization_url_builder_rejects_missing_endpoint() -> None:
    with pytest.raises(ValueError, match="authorization_endpoint is required"):
        MetaInstagramAuthorizationUrlBuilder(
            client_id="app-123",
            authorization_endpoint="",
        )
