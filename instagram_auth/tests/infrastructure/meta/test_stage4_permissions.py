from datetime import UTC, datetime

from instagram_auth.baseline import InstagramPermission
from instagram_auth.infrastructure.meta.dto import MetaInstagramTokenDto
from instagram_auth.infrastructure.meta.mappers import MetaAuthorizationGrantMapper
from instagram_auth.infrastructure.meta.parsers import MetaTokenPayloadParser
from tests.application.contracts.fakes import FixedClock


def test_token_parser_reads_permission_list() -> None:
    dto = MetaTokenPayloadParser().parse(
        {
            "access_token": "token",
            "permissions": [
                "instagram_business_basic",
                "instagram_business_manage_messages",
            ],
        }
    )

    assert dto.permissions == frozenset(
        {"instagram_business_basic", "instagram_business_manage_messages"}
    )


def test_token_parser_reads_comma_separated_permissions() -> None:
    dto = MetaTokenPayloadParser().parse(
        {
            "access_token": "token",
            "permissions": "instagram_business_basic,instagram_business_manage_comments",
        }
    )

    assert dto.permissions == frozenset(
        {"instagram_business_basic", "instagram_business_manage_comments"}
    )


def test_grant_mapper_keeps_only_known_instagram_permissions() -> None:
    mapper = MetaAuthorizationGrantMapper(FixedClock(datetime(2026, 9, 3, tzinfo=UTC)))
    grant = mapper.map(
        MetaInstagramTokenDto(
            access_token="token",
            expires_in=None,
            permissions=frozenset({"instagram_business_basic", "future_provider_permission"}),
        )
    )

    assert grant.granted_permissions == frozenset({InstagramPermission.BASIC})
