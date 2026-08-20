import pytest

from identity.application.errors import InvalidIdentityValueError
from identity.domain import IdentityType
from identity.infrastructure.security.normalizer import DefaultIdentityNormalizer


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" +968 9000 0000 ", "+96890000000"),
        ("00968-9000-0000", "+96890000000"),
        ("+٩٦٨ ٩٠٠٠ ٠٠٠٠", "+96890000000"),
    ],
)
def test_mobile_normalization_produces_single_international_form(
    value: str,
    expected: str,
) -> None:
    normalizer = DefaultIdentityNormalizer()

    assert normalizer.normalize(IdentityType.MOBILE, value) == expected


def test_mobile_normalization_rejects_non_international_number() -> None:
    normalizer = DefaultIdentityNormalizer()

    with pytest.raises(InvalidIdentityValueError, match="E.164"):
        normalizer.normalize(IdentityType.MOBILE, "90000000")


def test_mobile_normalization_rejects_invalid_country_code() -> None:
    normalizer = DefaultIdentityNormalizer()

    with pytest.raises(InvalidIdentityValueError, match="E.164"):
        normalizer.normalize(IdentityType.MOBILE, "+0123456789")


@pytest.mark.parametrize(
    "value",
    [
        "+968\u200e90000000",
        "+968\u200f90000000",
    ],
)
def test_mobile_normalization_rejects_direction_control_characters(value: str) -> None:
    normalizer = DefaultIdentityNormalizer()

    with pytest.raises(InvalidIdentityValueError, match="E.164"):
        normalizer.normalize(IdentityType.MOBILE, value)


def test_email_normalization_applies_unicode_normalization_and_casefolding() -> None:
    normalizer = DefaultIdentityNormalizer()

    normalized = normalizer.normalize(IdentityType.EMAIL, " ＵＳＥＲ@Example.COM ")

    assert normalized == "user@example.com"


@pytest.mark.parametrize(
    "value",
    [
        "user example@example.com",
        "missing-at.example.com",
        "@example.com",
        "user@",
        "user@@example.com",
        "user\u200e@example.com",
        "user\u200f@example.com",
    ],
)
def test_email_normalization_rejects_invalid_values(value: str) -> None:
    normalizer = DefaultIdentityNormalizer()

    with pytest.raises(InvalidIdentityValueError):
        normalizer.normalize(IdentityType.EMAIL, value)
