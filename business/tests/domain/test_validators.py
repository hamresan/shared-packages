import pytest

from business.domain import (
    BusinessNameValidator,
    BusinessTypeValidator,
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageCodeValidator,
    TimeZoneValidator,
)


def test_business_name_validator_trims_outer_whitespace() -> None:
    assert BusinessNameValidator().validate("  My Business  ") == "My Business"


@pytest.mark.parametrize("name", ["", " \t ", "x" * 161])
def test_business_name_validator_rejects_invalid_names(name: str) -> None:
    with pytest.raises(ValueError, match="Business name"):
        BusinessNameValidator().validate(name)


def test_business_name_validator_accepts_maximum_length() -> None:
    assert BusinessNameValidator().validate("x" * 160) == "x" * 160


def test_country_code_validator_normalizes_ascii_code() -> None:
    assert CountryCodeValidator().validate(" om ") == "OM"


@pytest.mark.parametrize("country", ["", "O", "OMA", "عُ", "O1"])
def test_country_code_validator_rejects_invalid_codes(country: str) -> None:
    with pytest.raises(ValueError, match="Country code"):
        CountryCodeValidator().validate(country)


def test_currency_code_validator_normalizes_ascii_code() -> None:
    assert CurrencyCodeValidator().validate(" omr ") == "OMR"


@pytest.mark.parametrize("currency", ["", "OM", "OMRR", "ریال", "O1R"])
def test_currency_code_validator_rejects_invalid_codes(currency: str) -> None:
    with pytest.raises(ValueError, match="Currency code"):
        CurrencyCodeValidator().validate(currency)


def test_timezone_validator_accepts_iana_timezone() -> None:
    assert TimeZoneValidator().validate(" Asia/Muscat ") == "Asia/Muscat"


@pytest.mark.parametrize("timezone", ["", "   ", "Mars/Olympus"])
def test_timezone_validator_rejects_invalid_timezones(timezone: str) -> None:
    with pytest.raises(ValueError, match="Timezone"):
        TimeZoneValidator().validate(timezone)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(" EN ", "en"), ("en-US", "en-us"), ("zh-Hant", "zh-hant")],
)
def test_language_code_validator_accepts_common_language_tags(raw: str, expected: str) -> None:
    assert LanguageCodeValidator().validate(raw) == expected


@pytest.mark.parametrize("language", ["", " ", "123", "english", "e", "en_OM"])
def test_language_code_validator_rejects_invalid_tags(language: str) -> None:
    with pytest.raises(ValueError, match="Language"):
        LanguageCodeValidator().validate(language)


def test_business_type_validator_normalizes_optional_type() -> None:
    validator = BusinessTypeValidator()
    assert validator.validate("  BAKERY  ") == "bakery"
    assert validator.validate(None) is None
    assert validator.validate("  ") is None


def test_business_type_validator_rejects_excessive_length() -> None:
    with pytest.raises(ValueError, match="Business type"):
        BusinessTypeValidator().validate("x" * 81)
