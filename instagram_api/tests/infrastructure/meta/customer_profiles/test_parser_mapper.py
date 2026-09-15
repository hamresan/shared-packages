"""Meta customer profile parser and mapper tests."""

import pytest

from instagram_api.domain import InstagramUserId
from instagram_api.infrastructure.meta.customer_profiles import (
    MetaInstagramCustomerProfileMapper,
    MetaInstagramCustomerProfilePayloadParser,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


def test_parser_and_mapper_preserve_supported_customer_profile_fields() -> None:
    parser = MetaInstagramCustomerProfilePayloadParser()
    mapper = MetaInstagramCustomerProfileMapper()

    dto = parser.parse(
        {
            "id": "1234567890",
            "username": "customer",
            "name": "Customer Name",
            "profile_pic": "https://example.com/profile.jpg",
        }
    )
    profile = mapper.to_domain(dto)

    assert profile.id == InstagramUserId("1234567890")
    assert profile.username == "customer"
    assert profile.name == "Customer Name"
    assert profile.profile_picture_url == "https://example.com/profile.jpg"


def test_parser_normalizes_missing_or_invalid_optional_fields_to_none() -> None:
    dto = MetaInstagramCustomerProfilePayloadParser().parse(
        {
            "id": "customer",
            "username": 123,
            "name": "",
            "profile_pic": False,
        }
    )

    assert dto.username is None
    assert dto.name is None
    assert dto.profile_picture_url is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"id": ""},
        {"id": 123},
    ],
)
def test_parser_rejects_missing_or_invalid_customer_id(
    payload: dict[str, object],
) -> None:
    with pytest.raises(MetaInvalidResponseError):
        MetaInstagramCustomerProfilePayloadParser().parse(payload)
