"""Meta account payload parser and mapper tests."""

import pytest

from instagram_api.domain import InstagramAccountId
from instagram_api.infrastructure.meta.accounts import (
    MetaInstagramAccountMapper,
    MetaInstagramAccountPayloadParser,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


def test_parser_and_mapper_preserve_supported_profile_fields() -> None:
    parser = MetaInstagramAccountPayloadParser()
    mapper = MetaInstagramAccountMapper()

    dto = parser.parse(
        {
            "user_id": "17841400000000000",
            "username": "shop",
            "name": "Shop Name",
            "biography": "Bio",
            "website": "https://example.com",
            "profile_picture_url": "https://example.com/profile.jpg",
            "followers_count": 120,
            "follows_count": 30,
            "media_count": 42,
        }
    )
    account = mapper.to_domain(dto)

    assert account.id == InstagramAccountId("17841400000000000")
    assert account.username == "shop"
    assert account.name == "Shop Name"
    assert account.biography == "Bio"
    assert account.website == "https://example.com"
    assert account.profile_picture_url == "https://example.com/profile.jpg"
    assert account.followers_count == 120
    assert account.follows_count == 30
    assert account.media_count == 42


def test_parser_normalizes_invalid_optional_fields_to_none() -> None:
    dto = MetaInstagramAccountPayloadParser().parse(
        {
            "user_id": "account",
            "username": "shop",
            "name": 1,
            "followers_count": True,
            "media_count": "42",
        }
    )

    assert dto.name is None
    assert dto.followers_count is None
    assert dto.media_count is None


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "shop"},
        {"user_id": "account"},
        {"user_id": "", "username": "shop"},
        {"user_id": "account", "username": ""},
    ],
)
def test_parser_rejects_missing_required_profile_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(MetaInvalidResponseError):
        MetaInstagramAccountPayloadParser().parse(payload)
