import pytest

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.infrastructure.meta.parsers import (
    MetaIdentityPayloadParser,
    MetaTokenPayloadParser,
)


def test_token_parser_accepts_token_without_expiry() -> None:
    result = MetaTokenPayloadParser().parse({"access_token": "token"})
    assert result.access_token == "token"
    assert result.expires_in is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"access_token": ""},
        {"access_token": "token", "expires_in": "3600"},
    ],
)
def test_token_parser_rejects_invalid_payload(payload: dict[str, object]) -> None:
    with pytest.raises(InstagramProviderError):
        MetaTokenPayloadParser().parse(payload)


def test_identity_parser_rejects_missing_required_field() -> None:
    with pytest.raises(InstagramProviderError):
        MetaIdentityPayloadParser().parse({"user_id": "ig-1", "username": "shop"})
